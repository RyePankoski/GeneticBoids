import pygame
from constants import *
import random
import math
from pygame import mixer
from star import Star
from utility import *


class BoundingStar:
    def __init__(self, screen):
        mixer.init
        self.screen = screen
        self.stars = []
        self.stars_total = 3

        # 3-5 is a good range for the scalar

        scalar = 2

        speed = 1 * scalar
        self.adjust_rate = .01
        self.repel_rate = 0.007

        self.repel_distance = 6 * scalar
        self.align_distance = 16 * scalar

        BASE_STARS = 1000
        self.max_stars = int(BASE_STARS / scalar)
        print(f"{self.max_stars}")

        self.sector_size = 8 * scalar
        print(f"{self.sector_size}")

        self.global_average_color = None
        self.global_green = 0
        self.global_red = 0
        self.global_blue = 0
        self.global_pos_x = WINDOW_WIDTH / 2
        self.global_pos_y = WINDOW_HEIGHT / 2
        self.global_angle = 0
        self.pop = pygame.mixer.Sound("pop.mp3")
        self.total_reds = 0
        self.total_blues = 0
        self.total_greens = 0
        self.total_grays = 0
        self.total_operations = 0

        self.num_cols = math.ceil(WINDOW_WIDTH / self.sector_size)
        self.num_rows = math.ceil(WINDOW_HEIGHT / self.sector_size)
        self.grid_cells = [[set() for _ in range(self.num_cols)] for _ in range(self.num_rows)]

        random_dx = random.uniform(-1, 1)
        random_dy = random.uniform(-1, 1)

        magnitude = math.sqrt(random_dx * random_dx + random_dy * random_dy)

        if magnitude != 0:
            random_dx /= magnitude
            random_dy /= magnitude

        self.red_star = Star(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, random_dx, random_dy, speed, (255, 0, 0), 100,
                             prefered_gene='r', solitude_tolerance=500)
        self.green_star = Star(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, random_dx, random_dy, speed, (0, 255, 0),
                               100,
                               prefered_gene='g', solitude_tolerance=500)
        self.blue_star = Star(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, random_dx, random_dy, speed, (0, 0, 255), 100,
                              prefered_gene='b', solitude_tolerance=500)
        self.stars.append(self.red_star)
        self.stars.append(self.green_star)
        self.stars.append(self.blue_star)

    def update(self):
        self.recalculate_totals()
        self._control_population()
        self.total_operations = 0

        stars_to_remove = []
        stars_who_died_alone = []

        for star in self.stars:
            self._update_star_position(star)

        for star in self.stars[:]:  # Create a copy of the list to safely modify it
            death_status = self._handle_star_interactions(star)
            if death_status == "natural_death":
                stars_to_remove.append(star)
            elif death_status == "solitude_death":
                stars_who_died_alone.append(star)

        # Handle dead stars
        for star in stars_to_remove:
            if star in self.stars:
                self.stars_die(star)
        for star in stars_who_died_alone:
            if star in self.stars:
                self.die_alone(star)

        self._handle_operations_overload()

    def get_adjacent_sectors(self, row, col):
        adjacent_stars = set()

        # Calculate bounds with direct clamping
        start_row = max(0, row - 1)
        end_row = min(self.num_rows, row + 3)
        start_col = max(0, col - 1)
        end_col = min(self.num_cols, col + 3)

        # Use direct slice of grid cells
        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                if self.grid_cells[r][c]:  # Only update if the cell has stars
                    adjacent_stars.update(self.grid_cells[r][c])

        return adjacent_stars

    def update_star_sector(self, star, old_pos=None):
        # Handle removal from old position
        if old_pos:
            old_col = int(old_pos[0] // self.sector_size)
            old_row = int(old_pos[1] // self.sector_size)
            if 0 <= old_row < self.num_rows and 0 <= old_col < self.num_cols:
                # Safely remove star if it exists in the old cell
                try:
                    self.grid_cells[old_row][old_col].remove(star)
                except KeyError:
                    pass  # Star wasn't in this cell, which is fine

        # Add to new position
        new_col = int(star.pos_x // self.sector_size)
        new_row = int(star.pos_y // self.sector_size)

        new_col = max(0, min(new_col, self.num_cols - 1))
        new_row = max(0, min(new_row, self.num_rows - 1))

        # Add to new cell
        self.grid_cells[new_row][new_col].add(star)

    def check_interactions(self, star, nearby_stars):
        align_distance_sq = self.align_distance * self.align_distance
        repel_distance_sq = self.repel_distance * self.repel_distance

        saw_any_stars = False
        saw_enemy_stars = False

        for other_star in nearby_stars:
            if other_star is star:
                continue

            dx = other_star.pos_x - star.pos_x
            dy = other_star.pos_y - star.pos_y
            distance_sq = dx * dx + dy * dy

            self.total_operations += 1
            genetically_compatible = (star.gene_preference == other_star.gene_preference)

            if genetically_compatible:
                saw_any_stars = True

                if distance_sq < repel_distance_sq:
                    adjust_vector_farther(star, other_star, self.adjust_rate)
                elif distance_sq < align_distance_sq:
                    adjust_vector_closer(star, other_star, self.adjust_rate)
            else:
                saw_enemy_stars = True
                repel_diff_genes(star, other_star, self.repel_rate)

        if saw_enemy_stars:
            saw_cohesion_stars = apply_cohesion(star, nearby_stars,.008)
        else:
            saw_cohesion_stars = apply_cohesion(star, nearby_stars,.004)

        saw_any_stars = saw_any_stars or saw_cohesion_stars

        if saw_any_stars:
            star.time_alone = 0
        else:
            star.time_alone += 1

    def _control_population(self):
        while len(self.stars) > self.max_stars:
            star_to_remove = random.choice(self.stars)
            if star_to_remove in self.stars:
                # Update counts before removing
                if star_to_remove.gene_preference == "r":
                    self.total_reds -= 1
                elif star_to_remove.gene_preference == "g":
                    self.total_greens -= 1
                elif star_to_remove.gene_preference == "b":
                    self.total_blues -= 1

                self.stars.remove(star_to_remove)
                self.stars_total = len(self.stars)

                # Remove from grid
                current_row = int(star_to_remove.pos_y // self.sector_size)
                current_col = int(star_to_remove.pos_x // self.sector_size)
                if 0 <= current_row < self.num_rows and 0 <= current_col < self.num_cols:
                    try:
                        self.grid_cells[current_row][current_col].remove(star_to_remove)
                    except KeyError:
                        pass

    def _update_star_position(self, star):
        magnitude = math.sqrt(star.dx * star.dx + star.dy * star.dy)
        if magnitude != 0:
            star.dx = star.dx / magnitude
            star.dy = star.dy / magnitude
        old_pos = (star.pos_x, star.pos_y)

        star.pos_x += star.dx * star.velocity
        star.pos_y += star.dy * star.velocity

        handle_boundaries(star)
        self.update_star_sector(star, old_pos)

        return old_pos

    def _handle_star_interactions(self, star):
        current_row = int(star.pos_y // self.sector_size)
        current_col = int(star.pos_x // self.sector_size)

        nearby_stars = self.get_adjacent_sectors(current_row, current_col)
        self.check_interactions(star, nearby_stars)

        star.lifetime += 1
        if star.lifetime > star.lifespan:
            return "natural_death"
        elif star.time_alone > star.solitude_tolerance and self.stars_total >= 50:
            return "solitude_death"
        else:
            star.size = (star.lifetime / 100) + 1
            return None

    def _handle_operations_overload(self):
        if self.total_operations > 35000:
            num_to_remove = max(1, int(self.stars_total * 0.1))
            for _ in range(num_to_remove):
                if len(self.stars) > 50:  # Keep a minimum population
                    star_to_remove = random.choice(self.stars)
                    if star_to_remove in self.stars:
                        self.stars.remove(star_to_remove)
                        self.stars_total = len(self.stars)
                        current_row = int(star_to_remove.pos_y // self.sector_size)
                        current_col = int(star_to_remove.pos_x // self.sector_size)
                        if 0 <= current_row < self.num_rows and 0 <= current_col < self.num_cols:
                            try:
                                self.grid_cells[current_row][current_col].remove(star_to_remove)
                            except KeyError:
                                pass

    def stars_die(self, star):
        star_gene = star.gene_preference

        pygame.draw.line(self.screen, (255, 255, 255),
                         (star.pos_x - 10, star.pos_y - 10),
                         (star.pos_x + 10, star.pos_y + 10), 2)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (star.pos_x - 10, star.pos_y + 10),
                         (star.pos_x + 10, star.pos_y - 10), 2)

        # Remove the star first
        if star in self.stars:
            self.stars.remove(star)

        # Update counts
        if star_gene == "r":
            self.total_reds -= 1
        elif star_gene == "g":
            self.total_greens -= 1
        elif star_gene == "b":
            self.total_blues -= 1

        if not (0 <= star.pos_x <= WINDOW_WIDTH and 0 <= star.pos_y <= WINDOW_HEIGHT):
            return

        star_gene = star.gene_preference

        if (star_gene == "r" and self.total_reds > self.max_stars / 1.5) or \
                (star_gene == "g" and self.total_greens > self.max_stars / 1.5) or \
                (star_gene == "b" and self.total_blues > self.max_stars / 1.5):
            return

        if star_gene == "r" and self.total_reds < self.max_stars/5:
            for _ in range(4):  # More readable than repeated calls
                self.add_star(star)
        elif star_gene == "g" and self.total_greens < self.max_stars/5:
            for _ in range(4):
                self.add_star(star)
        elif star_gene == "b" and self.total_blues < self.max_stars/5:
            for _ in range(4):
                self.add_star(star)
        else:
            for _ in range(2):
                self.add_star(star)


    def die_alone(self, star):
        if self.stars_total < 50:
            return

        star_gene = star.gene_preference

        # Remove star first
        if star in self.stars:
            self.stars.remove(star)

        # Update counts
        if star_gene == "r":
            self.total_reds -= 1
        elif star_gene == "g":
            self.total_greens -= 1
        elif star_gene == "b":
            self.total_blues -= 1

        self.stars_total = len(self.stars)

        pygame.draw.line(self.screen, (255, 255, 255),
                         (star.pos_x - 10, star.pos_y - 10),
                         (star.pos_x + 10, star.pos_y + 10), 2)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (star.pos_x - 10, star.pos_y + 10),
                         (star.pos_x + 10, star.pos_y - 10), 2)

    def add_star(self, parent_star):
        if self.stars_total >= self.max_stars:
            return

        angle = random.uniform(-0.5, 0.5)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        new_dx = parent_star.dx * cos_a - parent_star.dy * sin_a
        new_dy = parent_star.dx * sin_a + parent_star.dy * cos_a

        r, g, b, preferred_gene, lifespan, solitude_tolerance = self.handle_genes(parent_star)

        new_star = Star(parent_star.pos_x, parent_star.pos_y, new_dx, new_dy,
                        parent_star.velocity, (r, g, b), lifespan, preferred_gene,
                        solitude_tolerance=solitude_tolerance)
        new_star.gene_preference = preferred_gene
        self.stars.append(new_star)
        self.update_star_sector(new_star)

        # Update totals after adding star
        if preferred_gene == "r":
            self.total_reds += 1
        elif preferred_gene == "g":
            self.total_greens += 1
        elif preferred_gene == "b":
            self.total_blues += 1
        self.stars_total = len(self.stars)

    def handle_lifespan_genes(self, new_gene):

        child_lifespan = random.uniform(0, 1200)

        if new_gene == "r" and self.total_reds < 20:
            solitude_tolerance = 300
        elif new_gene == "g" and self.total_greens < 20:
            solitude_tolerance = 300
        elif new_gene == "b" and self.total_blues < 20:
            solitude_tolerance = 300
        else:
            solitude_tolerance = 30

        return child_lifespan, solitude_tolerance

    def update_color_globals(self, new_gene):
        if new_gene == "r":
            self.total_reds += 1
        if new_gene == "g":
            self.total_greens += 1
        if new_gene == "b":
            self.total_blues += 1

        color_map = {
            self.total_reds: "Red",
            self.total_blues: "Blue",
            self.total_greens: "Green",
        }

        max_count = max(self.total_reds, self.total_blues, self.total_greens)
        self.global_average_color = color_map[max_count]

    def handle_color_gene(self, parent_star):
        parent_gene = parent_star.gene_preference
        color_drift_strength = 50
        gene_bias = 10
        survival_pressure = 10

        r, g, b = parent_star.color

        if parent_gene == "r":
            r += gene_bias
        if parent_star == "g":
            g += gene_bias
        if parent_gene == "b":
            b += gene_bias

        if self.total_reds < self.max_stars/5 and parent_star.gene_preference == "r":
            r += survival_pressure
        elif self.total_greens < self.max_stars/5 and parent_star.gene_preference == "g":
            g += survival_pressure
        elif self.total_blues < self.max_stars/5 and parent_star.gene_preference == "b":
            b += survival_pressure

        r = int(max(0, min(255, r + random.uniform(-color_drift_strength, color_drift_strength))))
        g = int(max(0, min(255, g + random.uniform(-color_drift_strength, color_drift_strength))))
        b = int(max(0, min(255, b + random.uniform(-color_drift_strength, color_drift_strength))))

        if r >= g and r >= b:
            preferred_gene = "r"
        elif g >= r and g >= b:
            preferred_gene = "g"
        else:
            preferred_gene = "b"

        self.update_color_globals(preferred_gene)
        return r, g, b, preferred_gene

    def handle_genes(self, parent_star):
        r, g, b, preferred_gene = self.handle_color_gene(parent_star)
        lifespan, solitude_tolerance = self.handle_lifespan_genes(preferred_gene)
        return r, g, b, preferred_gene, lifespan, solitude_tolerance

    def draw(self):
        self.update()
        self.draw_sector_grid()
        self._draw_star()
        self.draw_data()

    def _draw_star(self):
        for star in self.stars:
            pygame.draw.circle(self.screen, star.color, (star.pos_x, star.pos_y), star.size)

    def draw_data(self):
        # Font setup for drawing text
        font = pygame.font.Font(None, 36)
        y_offset = 10  # Starting y position
        x_position = 10  # Left margin
        line_spacing = 30  # Space between lines

        # Draw total operations
        ops_text = f"Operations: {self.total_operations}"
        ops_surface = font.render(ops_text, True, (255, 255, 255))
        self.screen.blit(ops_surface, (x_position, y_offset))

        # Draw n^2 (stars_total squared)
        n_squared = self.stars_total * self.stars_total
        n2_text = f"N²: {n_squared}"
        n2_surface = font.render(n2_text, True, (255, 255, 255))
        self.screen.blit(n2_surface, (x_position, y_offset + line_spacing))

        # Draw total reds
        reds_text = f"Red Stars: {self.total_reds}"
        reds_surface = font.render(reds_text, True, (255, 100, 100))
        self.screen.blit(reds_surface, (x_position, y_offset + line_spacing * 2))

        # Draw total greens
        greens_text = f"Green Stars: {self.total_greens}"
        greens_surface = font.render(greens_text, True, (100, 255, 100))
        self.screen.blit(greens_surface, (x_position, y_offset + line_spacing * 3))

        # Draw total blues
        blues_text = f"Blue Stars: {self.total_blues}"
        blues_surface = font.render(blues_text, True, (100, 100, 255))
        self.screen.blit(blues_surface, (x_position, y_offset + line_spacing * 4))

        # Draw total stars
        total_text = f"Total Stars: {self.stars_total}"
        total_surface = font.render(total_text, True, (255, 255, 255))
        self.screen.blit(total_surface, (x_position, y_offset + line_spacing * 5))

    def draw_sector_grid(self):
        GRID_COLOR = (20, 20, 20)

        for col in range(self.num_cols + 1):
            x = col * self.sector_size
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (x, 0),
                (x, WINDOW_HEIGHT),
                2  # Thicker line
            )

        # Draw horizontal lines
        for row in range(self.num_rows + 1):
            y = row * self.sector_size
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (0, y),
                (WINDOW_WIDTH, y),
                2  # Thicker line
            )

    def recalculate_totals(self):
        """Recalculate total counts for all star types"""
        self.total_reds = sum(1 for star in self.stars if star.gene_preference == "r")
        self.total_greens = sum(1 for star in self.stars if star.gene_preference == "g")
        self.total_blues = sum(1 for star in self.stars if star.gene_preference == "b")
        self.stars_total = len(self.stars)
