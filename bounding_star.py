import pygame
from constants import *
import random
import math
from pygame import mixer


class Star:
    def __init__(self, pos_x=None, pos_y=None, dx=None, dy=None, velocity=None, color=None, lifespan=None,
                 prefered_gene=None, solitude_tolerance=None):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dx = dx
        self.dy = dy
        self.velocity = velocity
        self.color = color
        self.size = 1
        self.lifetime = 0
        self.lifespan = lifespan
        self.gene_preference = prefered_gene
        self.health_points = 200
        self.solitude_tolerance = solitude_tolerance
        self.time_alone = 0


class BoundingStar:
    def __init__(self, screen):
        mixer.init
        self.screen = screen
        self.stars = []
        self.stars_total = 3

        scalar = 5

        random_speed = 1 * scalar
        self.adjust_rate = .01
        self.repel_rate = 0.008

        self.repel_distance = 30
        self.align_distance = 80

        # self.center_attraction_strength = 0.01
        self.center_attraction_strength = .005
        self.vector_alignment_strength = .03

        self.max_stars = 200



        self.red_center = {'x': WINDOW_WIDTH / 2, 'y': WINDOW_HEIGHT / 2}
        self.blue_center = {'x': WINDOW_WIDTH / 2, 'y': WINDOW_HEIGHT / 2}
        self.green_center = {'x': WINDOW_WIDTH / 2, 'y': WINDOW_HEIGHT / 2}

        self.red_vector = {'dx': 0, 'dy': 0}
        self.blue_vector = {'dx': 0, 'dy': 0}
        self.green_vector = {'dx': 0, 'dy': 0}

        self.global_average_color = None
        self.global_average_vector = None
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


        self.sector_size = 40  # Based on our previous discussion
        self.num_cols = math.ceil(WINDOW_WIDTH / self.sector_size)
        self.num_rows = math.ceil(WINDOW_HEIGHT / self.sector_size)
        self.grid_cells = [[set() for _ in range(self.num_cols)] for _ in range(self.num_rows)]

        random_dx = random.uniform(-1, 1)
        random_dy = random.uniform(-1, 1)

        magnitude = math.sqrt(random_dx * random_dx + random_dy * random_dy)
        if magnitude != 0:
            random_dx /= magnitude
            random_dy /= magnitude

        self.red_star = Star(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, random_dx, random_dy, random_speed, (255, 0, 0), 100,
                             prefered_gene='r', solitude_tolerance=500)
        self.green_star = Star(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, random_dx, random_dy, random_speed, (0, 255, 0),
                               100,
                               prefered_gene='g', solitude_tolerance=500)
        self.blue_star = Star(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, random_dx, random_dy, random_speed, (0, 0, 255), 100,
                              prefered_gene='b', solitude_tolerance=500)
        self.stars.append(self.red_star)
        self.stars.append(self.green_star)
        self.stars.append(self.blue_star)

    def normalize_vector(self, dx, dy):
        magnitude = math.sqrt(dx * dx + dy * dy)
        if magnitude != 0:
            return dx / magnitude, dy / magnitude
        return 0, 0

    def adjust_vector_closer(self, star, near_star):
        current_speed = math.sqrt(star.dx * star.dx + star.dy * star.dy)

        # Calculate direction adjustment
        new_dx = star.dx + (near_star.dx - star.dx) * self.adjust_rate
        new_dy = star.dy + (near_star.dy - star.dy) * self.adjust_rate

        # Normalize and restore original speed
        normalized_dx, normalized_dy = self.normalize_vector(new_dx, new_dy)
        star.dx = normalized_dx * current_speed
        star.dy = normalized_dy * current_speed

    def repel_diff_genes(self, star, near_star):

        current_speed = math.sqrt(star.dx * star.dx + star.dy * star.dy)

        # Calculate repulsion vector (opposite to the direction to neighbor)
        repel_dx = star.pos_x - near_star.pos_x
        repel_dy = star.pos_y - near_star.pos_y

        # Normalize repulsion vector
        repel_dx, repel_dy = self.normalize_vector(repel_dx, repel_dy)

        # Apply repulsion while maintaining speed
        new_dx = star.dx + repel_dx * self.repel_rate
        new_dy = star.dy + repel_dy * self.repel_rate

        # Normalize and restore original speed
        normalized_dx, normalized_dy = self.normalize_vector(new_dx, new_dy)
        star.dx = normalized_dx * current_speed
        star.dy = normalized_dy * current_speed

    def adjust_vector_farther(self, star, near_star):
        current_speed = math.sqrt(star.dx * star.dx + star.dy * star.dy)

        # Calculate repulsion vector (opposite to the direction to neighbor)
        repel_dx = star.pos_x - near_star.pos_x
        repel_dy = star.pos_y - near_star.pos_y

        # Normalize repulsion vector
        repel_dx, repel_dy = self.normalize_vector(repel_dx, repel_dy)

        # Apply repulsion while maintaining speed
        new_dx = star.dx + repel_dx * self.adjust_rate
        new_dy = star.dy + repel_dy * self.adjust_rate

        # Normalize and restore original speed
        normalized_dx, normalized_dy = self.normalize_vector(new_dx, new_dy)
        star.dx = normalized_dx * current_speed
        star.dy = normalized_dy * current_speed

    def get_sector_for_position(self, x, y):
        col = int(x // self.sector_size)
        row = int(y // self.sector_size)
        return (row, col)

    def get_adjacent_sectors(self, row, col):
        """
        Get stars from adjacent sectors more efficiently.
        """
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

        # Ensure we stay within grid bounds
        new_col = max(0, min(new_col, self.num_cols - 1))
        new_row = max(0, min(new_row, self.num_rows - 1))

        # Add to new cell
        self.grid_cells[new_row][new_col].add(star)

    def update_species_centers(self):
        """Calculate center of mass for each species"""
        red_total = {'x': 0, 'y': 0, 'count': 0}
        blue_total = {'x': 0, 'y': 0, 'count': 0}
        green_total = {'x': 0, 'y': 0, 'count': 0}

        for star in self.stars:
            if star.gene_preference == 'r':
                red_total['x'] += star.pos_x
                red_total['y'] += star.pos_y
                red_total['count'] += 1
            elif star.gene_preference == 'b':
                blue_total['x'] += star.pos_x
                blue_total['y'] += star.pos_y
                blue_total['count'] += 1
            elif star.gene_preference == 'g':
                green_total['x'] += star.pos_x
                green_total['y'] += star.pos_y
                green_total['count'] += 1

        # Update centers if species exists
        if red_total['count'] > 0:
            self.red_center = {
                'x': red_total['x'] / red_total['count'],
                'y': red_total['y'] / red_total['count']
            }
        if blue_total['count'] > 0:
            self.blue_center = {
                'x': blue_total['x'] / blue_total['count'],
                'y': blue_total['y'] / blue_total['count']
            }
        if green_total['count'] > 0:
            self.green_center = {
                'x': green_total['x'] / green_total['count'],
                'y': green_total['y'] / green_total['count']
            }

    def attract_to_species_center(self, star):
        """Apply force towards species center with catch-up mechanism"""
        if star.gene_preference not in ['r', 'g', 'b']:
            return

        # Get appropriate center based on gene preference
        center = {
            'r': self.red_center,
            'g': self.green_center,
            'b': self.blue_center
        }[star.gene_preference]

        # Calculate direction to center
        dx = center['x'] - star.pos_x
        dy = center['y'] - star.pos_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance

            # Apply attraction force towards the center
            star.dx += dx * self.center_attraction_strength
            star.dy += dy * self.center_attraction_strength

        # Normalize final velocity
        magnitude = math.sqrt(star.dx * star.dx + star.dy * star.dy)
        if magnitude > 0:
            star.dx = star.dx / magnitude
            star.dy = star.dy / magnitude

    def check_interactions(self, star, nearby_stars):
        align_distance_sq = self.align_distance * self.align_distance
        repel_distance_sq = self.repel_distance * self.repel_distance

        # New cohesion parameters
        cohesion_distance = 100  # Distance within which boids try to stay together
        cohesion_strength = 0.001  # Strength of the cohesion force

        # Initialize variables for cohesion
        center_x = 0
        center_y = 0
        num_neighbors = 0

        saw_any_stars = False
        same_gene_stars = [s for s in nearby_stars if s is not star and s.gene_preference == star.gene_preference]

        for other_star in nearby_stars:
            if other_star is star:
                continue

            dx = other_star.pos_x - star.pos_x
            dy = other_star.pos_y - star.pos_y
            distance_sq = dx * dx + dy * dy

            # Skip if too far for any interaction
            if distance_sq > cohesion_distance * cohesion_distance:
                continue

            self.total_operations += 1

            # Check genetic compatibility
            genetically_compatible = (star.gene_preference == other_star.gene_preference)

            if genetically_compatible:
                saw_any_stars = True
                # Add to center of mass calculation for cohesion
                center_x += other_star.pos_x
                center_y += other_star.pos_y
                num_neighbors += 1

                # Handle alignment and repulsion
                if distance_sq < repel_distance_sq:
                    self.adjust_vector_farther(star, other_star)
                elif distance_sq < align_distance_sq:
                    self.adjust_vector_closer(star, other_star)
            else:
                # Non-compatible stars still repel
                self.repel_diff_genes(star, other_star)

        # Apply cohesion force if we have neighbors
        if num_neighbors > 0:
            # Calculate center of mass of neighbors
            center_x /= num_neighbors
            center_y /= num_neighbors

            # Calculate direction to center of mass
            to_center_x = center_x - star.pos_x
            to_center_y = center_y - star.pos_y

            # Normalize direction
            distance = math.sqrt(to_center_x * to_center_x + to_center_y * to_center_y)
            if distance > 0:
                to_center_x /= distance
                to_center_y /= distance

                # Apply cohesion force
                star.dx += to_center_x * cohesion_strength
                star.dy += to_center_y * cohesion_strength

                # Normalize final velocity
                magnitude = math.sqrt(star.dx * star.dx + star.dy * star.dy)
                if magnitude > 0:
                    star.dx = star.dx / magnitude
                    star.dy = star.dy / magnitude

        # Update time_alone based on whether we saw any genetically compatible stars
        if saw_any_stars:
            star.time_alone = 0
        else:
            star.time_alone += 1

    def _control_population(self):
        """Manage population size to stay within max_stars limit"""
        while len(self.stars) > self.max_stars:
            star_to_remove = random.choice(self.stars)
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
        """Update individual star position and handle boundaries"""
        # Normalize direction vector
        magnitude = math.sqrt(star.dx * star.dx + star.dy * star.dy)
        if magnitude != 0:
            star.dx = star.dx / magnitude
            star.dy = star.dy / magnitude

        # Store old position for grid update
        old_pos = (star.pos_x, star.pos_y)

        # Update position
        star.pos_x += star.dx * star.velocity
        star.pos_y += star.dy * star.velocity

        # Handle boundaries
        self._handle_boundaries(star)

        # Update center attraction and grid position
        self.attract_to_species_center(star)
        self.update_star_sector(star, old_pos)

        return old_pos

    def _handle_boundaries(self, star):
        """Handle star interaction with screen boundaries"""
        # Edge avoidance
        edge_threshold = 50
        steer_strength = 0.05

        # Basic edge avoidance
        if star.pos_x < edge_threshold:
            star.dx += steer_strength
        elif star.pos_x > WINDOW_WIDTH - edge_threshold:
            star.dx -= steer_strength

        if star.pos_y < edge_threshold:
            star.dy += steer_strength
        elif star.pos_y > WINDOW_HEIGHT - edge_threshold:
            star.dy -= steer_strength

        # Corner avoidance
        corner_margin = 400
        max_corner_force = 0.4

        dist_top_left = math.sqrt(star.pos_x ** 2 + star.pos_y ** 2)
        dist_top_right = math.sqrt((WINDOW_WIDTH - star.pos_x) ** 2 + star.pos_y ** 2)
        dist_bottom_left = math.sqrt(star.pos_x ** 2 + (WINDOW_HEIGHT - star.pos_y) ** 2)
        dist_bottom_right = math.sqrt((WINDOW_WIDTH - star.pos_x) ** 2 + (WINDOW_HEIGHT - star.pos_y) ** 2)

        if dist_top_left < corner_margin:
            force = max_corner_force * (1 - dist_top_left / corner_margin)
            star.dx += force
            star.dy += force
        elif dist_top_right < corner_margin:
            force = max_corner_force * (1 - dist_top_right / corner_margin)
            star.dx -= force
            star.dy += force
        elif dist_bottom_left < corner_margin:
            force = max_corner_force * (1 - dist_bottom_left / corner_margin)
            star.dx += force
            star.dy -= force
        elif dist_bottom_right < corner_margin:
            force = max_corner_force * (1 - dist_bottom_right / corner_margin)
            star.dx -= force
            star.dy -= force

        # Normalize final velocity
        magnitude = math.sqrt(star.dx * star.dx + star.dy * star.dy)
        if magnitude != 0:
            star.dx = star.dx / magnitude
            star.dy = star.dy / magnitude

    def _handle_star_interactions(self, star):
        """Handle star interactions and update lifetime/death status"""
        current_row = int(star.pos_y // self.sector_size)
        current_col = int(star.pos_x // self.sector_size)

        nearby_stars = self.get_adjacent_sectors(current_row, current_col)
        self.check_interactions(star, nearby_stars)

        star.lifetime += 1

        # Return death status
        if star.lifetime > star.lifespan:
            return "natural_death"
        elif star.time_alone > star.solitude_tolerance and self.stars_total > 50:
            return "solitude_death"
        else:
            star.size = star.lifetime/100
            return None

    def _update_global_stats(self, total_x, total_y, total_dx, total_dy, active_stars):
        """Update global statistics for the star system"""
        if active_stars > 0:
            self.global_pos_x = total_x / active_stars
            self.global_pos_y = total_y / active_stars

            avg_dx = total_dx / active_stars
            avg_dy = total_dy / active_stars
            self.global_angle = math.atan2(avg_dy, avg_dx)

    def _handle_performance_optimization(self):
        """Handle performance optimization when operation count is too high"""
        if self.total_operations > 30000:
            num_to_remove = max(1, int(self.stars_total * 0.1))
            for _ in range(num_to_remove):
                if len(self.stars) > 50:  # Keep a minimum population
                    star_to_remove = random.choice(self.stars)
                    if star_to_remove in self.stars:
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

    def update(self):
        """Main update function orchestrating all star updates and interactions"""
        self.update_species_centers()
        self._control_population()

        self.total_operations = 0
        total_x = total_y = total_dx = total_dy = 0
        active_stars = self.stars_total
        stars_to_remove = []
        stars_who_died_alone = []

        # First pass - update positions and collect statistics
        for star in self.stars:
            self._update_star_position(star)
            total_x += star.pos_x
            total_y += star.pos_y
            total_dx += star.dx
            total_dy += star.dy

        # Second pass - handle interactions and death
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

        # Update global statistics and handle performance
        self._update_global_stats(total_x, total_y, total_dx, total_dy, active_stars)
        self._handle_performance_optimization()

    def stars_die(self, star):
        star_gene = star.gene_preference
        self.stars_total -= 1

        pygame.draw.line(self.screen, (255, 255, 255),
                         (star.pos_x - 10, star.pos_y - 10),
                         (star.pos_x + 10, star.pos_y + 10), 2)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (star.pos_x - 10, star.pos_y + 10),
                         (star.pos_x + 10, star.pos_y - 10), 2)

        if star_gene == "r":
            self.total_reds -= 1
        if star_gene == "g":
            self.total_greens -= 1
        if star_gene == "b":
            self.total_blues -= 1

        if star.pos_x > WINDOW_WIDTH:
            self.stars.remove(star)
        elif star.pos_y > WINDOW_HEIGHT:
            self.stars.remove(star)
        elif star.pos_x < 0:
            self.stars.remove(star)
        elif star.pos_y < 0:
            self.stars.remove(star)
        else:
            self.add_star(star)
            self.add_star(star)
            self.stars.remove(star)

    def die_alone(self, star):
        star_gene = star.gene_preference

        if star_gene == "r":
            self.total_reds -= 1
        if star_gene == "g":
            self.total_greens -= 1
        if star_gene == "b":
            self.total_blues -= 1

        self.stars_total -= 1

        pygame.draw.line(self.screen, (255, 255, 255),
                         (star.pos_x - 10, star.pos_y - 10),
                         (star.pos_x + 10, star.pos_y + 10), 2)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (star.pos_x - 10, star.pos_y + 10),
                         (star.pos_x + 10, star.pos_y - 10), 2)

        self.stars.remove(star)

    def add_star(self, parent_star):

        if self.stars_total >= self.max_stars:
            return

        self.stars_total += 1

        # Add some randomness to the new star's direction while maintaining speed
        angle = random.uniform(-0.5, 0.5)  # Random angle adjustment in radians
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Rotate the velocity vector
        new_dx = parent_star.dx * cos_a - parent_star.dy * sin_a
        new_dy = parent_star.dx * sin_a + parent_star.dy * cos_a

        r, g, b, prefered_gene, lifespan = self.handle_genes(parent_star)

        # Adjust solitude tolerance based on the number of stars with the same gene preference
        if prefered_gene == 'r':
            same_gene_count = self.total_reds
        elif prefered_gene == 'g':
            same_gene_count = self.total_greens
        elif prefered_gene == 'b':
            same_gene_count = self.total_blues
        elif prefered_gene == 'mixed':
            same_gene_count = self.total_mixed
        elif prefered_gene == 'grey':
            same_gene_count = self.total_grays
        else:
            same_gene_count = 0

            #mamas

        if same_gene_count > 50:
            solitude_tolerance = 30  # 1 second = 30 frames (minimum tolerance)
        else:
            # Scale it up from 1 second (30 frames) to 40 seconds (1200 frames) based on group size
            solitude_tolerance = max(30, (50 - same_gene_count) * (1200 / 50))

            # Create the new star
        new_star = Star(parent_star.pos_x, parent_star.pos_y, new_dx, new_dy,
                        parent_star.velocity, (r, g, b), lifespan, prefered_gene, solitude_tolerance=solitude_tolerance)
        new_star.gene_preference = prefered_gene  # Actually set the gene preference
        self.stars.append(new_star)
        self.update_star_sector(new_star)

    def handle_lifespan_genes(self, parent_star):
        child_lifespan = parent_star.lifespan
        child_lifespan = random.uniform(0, 1200)
        return child_lifespan

    def handle_color_gene(self, parent_star):
        color_drift_strength = 20
        gene_pref_strength = 10

        r, g, b = parent_star.color
        self.global_red = (self.global_red * (self.stars_total - 1) + r) / self.stars_total
        self.global_green = (self.global_green * (self.stars_total - 1) + g) / self.stars_total
        self.global_blue = (self.global_blue * (self.stars_total - 1) + b) / self.stars_total

        total = r + g + b
        if total == 0:  # Prevent division by zero
            ratios = (0.33, 0.33, 0.33)
        else:
            ratios = (r / total, g / total, b / total)

        # Determine genetic marker based on dominant color ratio
        threshold = 0.4  # Color needs to be at least 40% to be considered dominant

        if max(ratios) < threshold:
            prefered_gene = "grey"
            self.total_grays += 1
        else:
            # Check for primary colors
            if ratios[0] > threshold:
                prefered_gene = "r"
                self.total_reds += 1
            elif ratios[1] > threshold:
                prefered_gene = "g"
                self.total_greens += 1
            elif ratios[2] > threshold:
                prefered_gene = "b"
                self.total_blues += 1
            else:
                prefered_gene = "None"

        # Calculate global average color based on total counts
        total_stars = (self.total_reds + self.total_blues +
                       self.total_greens + self.total_grays)

        if total_stars > 0:
            max_count = max(self.total_reds, self.total_blues,
                            self.total_greens, self.total_grays)

            if max_count == self.total_reds:
                self.global_average_color = "Red"
            elif max_count == self.total_blues:
                self.global_average_color = "Blue"
            elif max_count == self.total_greens:
                self.global_average_color = "Green"
            elif max_count == self.total_grays:
                self.global_average_color = "Grey"
        else:
            self.global_average_color = "None"

        if parent_star.gene_preference is not None:
            if parent_star.gene_preference == "r":
                r += gene_pref_strength
            elif parent_star.gene_preference == "g":
                g += gene_pref_strength
            elif parent_star.gene_preference == "b":
                b += gene_pref_strength

        # Calculate the color abundance
        red_ratio = self.total_reds / total_stars if total_stars > 0 else 0.33
        green_ratio = self.total_greens / total_stars if total_stars > 0 else 0.33
        blue_ratio = self.total_blues / total_stars if total_stars > 0 else 0.33

        # Amplify drift strength for under-represented colors
        r_drift = color_drift_strength * (1 + (1 - red_ratio) * 2)  # Stronger bias for under-represented reds
        g_drift = color_drift_strength * (1 + (1 - green_ratio) * 2)  # Stronger bias for under-represented greens
        b_drift = color_drift_strength * (1 + (1 - blue_ratio) * 2)  # Stronger bias for under-represented blues

        # Apply color drift based on the adjusted individual drift strengths
        r = int(r + random.uniform(-r_drift, r_drift))
        g = int(g + random.uniform(-g_drift, g_drift))
        b = int(b + random.uniform(-b_drift, b_drift))

        # Clamp values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        return r, g, b, prefered_gene

    def handle_genes(self, parent_star):
        r, g, b, prefered_gene = self.handle_color_gene(parent_star)
        lifespan = self.handle_lifespan_genes(parent_star)
        return r, g, b, prefered_gene, lifespan

    def min_max(self, number):
        return max(0, min(255, number))

    def update_species_vectors(self):
        """Calculate average movement vector for each species"""
        red_total = {'dx': 0, 'dy': 0, 'count': 0}
        blue_total = {'dx': 0, 'dy': 0, 'count': 0}
        green_total = {'dx': 0, 'dy': 0, 'count': 0}

        for star in self.stars:
            if star.gene_preference == 'r':
                red_total['dx'] += star.dx
                red_total['dy'] += star.dy
                red_total['count'] += 1
            elif star.gene_preference == 'b':
                blue_total['dx'] += star.dx
                blue_total['dy'] += star.dy
                blue_total['count'] += 1
            elif star.gene_preference == 'g':
                green_total['dx'] += star.dx
                green_total['dy'] += star.dy
                green_total['count'] += 1

        # Update vectors if species exists
        if red_total['count'] > 0:
            magnitude = math.sqrt(red_total['dx'] ** 2 + red_total['dy'] ** 2)
            if magnitude > 0:
                self.red_vector = {
                    'dx': red_total['dx'] / magnitude,
                    'dy': red_total['dy'] / magnitude
                }
        if blue_total['count'] > 0:
            magnitude = math.sqrt(blue_total['dx'] ** 2 + blue_total['dy'] ** 2)
            if magnitude > 0:
                self.blue_vector = {
                    'dx': blue_total['dx'] / magnitude,
                    'dy': blue_total['dy'] / magnitude
                }
        if green_total['count'] > 0:
            magnitude = math.sqrt(green_total['dx'] ** 2 + green_total['dy'] ** 2)
            if magnitude > 0:
                self.green_vector = {
                    'dx': green_total['dx'] / magnitude,
                    'dy': green_total['dy'] / magnitude
                }

    def align_with_species_vector(self, star):
        """Apply alignment force towards species average vector"""
        if star.gene_preference not in ['r', 'g', 'b']:
            return

        # Get appropriate vector
        vector = {
            'r': self.red_vector,
            'g': self.green_vector,
            'b': self.blue_vector
        }[star.gene_preference]

        # Update velocity with species alignment
        star.dx += vector['dx'] * self.vector_alignment_strength
        star.dy += vector['dy'] * self.vector_alignment_strength

        # Normalize final velocity
        magnitude = math.sqrt(star.dx * star.dx + star.dy * star.dy)
        if magnitude > 0:
            star.dx = star.dx / magnitude
            star.dy = star.dy / magnitude

    def draw(self):
        self.update()
        self.draw_sector_grid()
        self._draw_star()
        self.draw_average_color()
        self.draw_center_xs(self.screen)

    def draw_sector_grid(self):
        # Draw with more visible colors
        GRID_COLOR = (20, 20, 20)  # Brighter grey

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

    def draw_direction_line(self):
        # Define arrow properties
        line_length = 100
        arrow_head_size = 20

        # Calculate end point using average position and direction
        end_x = self.global_pos_x + math.cos(self.global_angle) * line_length
        end_y = self.global_pos_y + math.sin(self.global_angle) * line_length

        red = self.global_red
        green = self.global_green
        blue = self.global_blue

        arrow_color = red, green, blue

        # Draw main line
        pygame.draw.line(self.screen,
                         arrow_color,  # White color
                         (int(self.global_pos_x), int(self.global_pos_y)),  # Start point
                         (int(end_x), int(end_y)),  # End point
                         3)  # Line thickness

        # Calculate arrow head points
        # Create two lines at 30 degrees from main line
        left_angle = self.global_angle + math.radians(150)  # 150 degrees from forward
        right_angle = self.global_angle - math.radians(150)  # -150 degrees from forward

        # Calculate arrow head endpoints
        arrow_left_x = end_x + math.cos(left_angle) * arrow_head_size
        arrow_left_y = end_y + math.sin(left_angle) * arrow_head_size

        arrow_right_x = end_x + math.cos(right_angle) * arrow_head_size
        arrow_right_y = end_y + math.sin(right_angle) * arrow_head_size

        # Draw arrow head lines
        pygame.draw.line(self.screen,
                         arrow_color,
                         (int(end_x), int(end_y)),
                         (int(arrow_left_x), int(arrow_left_y)),
                         3)

        pygame.draw.line(self.screen,
                         arrow_color,
                         (int(end_x), int(end_y)),
                         (int(arrow_right_x), int(arrow_right_y)),
                         3)

    def draw_average_color(self):
        font = pygame.font.Font(None, 100)
        text = font.render(f"{self.global_average_color}", True, (self.global_red, self.global_green, self.global_blue))
        text_totals = font.render(
            f"{self.total_reds}, {self.total_greens}, {self.total_blues}, {self.total_grays}, total:{self.stars_total}/{self.max_stars}, opf:{self.total_operations}, n^2: {self.stars_total * self.stars_total}",
            True, WHITE)

        # Draw global average color text
        self.screen.blit(text, (10, 10))

        # Draw totals text to the right of global average
        totals_x = text.get_width() + 30  # Add some padding between texts
        self.screen.blit(text_totals, (totals_x, 10))

    def _draw_star(self):
        font = pygame.font.Font(None, 20)  # Small font size
        for star in self.stars:
            # Draw the star circle
            pygame.draw.circle(self.screen, star.color, (star.pos_x, star.pos_y), star.size)

            # if star.gene_preference:
            #     # Draw gene preference
            #     gene_text = font.render(f"{star.gene_preference}, {int(star.solitude_tolerance)}", True,
            #                             (255, 255, 255))
            #
            #     gene_x = star.pos_x - gene_text.get_width() / 2
            #     gene_y = star.pos_y - star.size - 20  # Moved up to make room for lifetime
            #     # Render both texts
            #     self.screen.blit(gene_text, (gene_x, gene_y))

    import pygame

    import pygame

    def draw_center_xs(self, screen):
        """Draws a color-coded X at the center of each color's center (red, green, blue)"""
        centers = {
            'r': self.red_center,
            'g': self.green_center,
            'b': self.blue_center
        }

        # Set colors for each X mark
        colors = {
            'r': (255, 0, 0),  # Red for the red center
            'g': (0, 255, 0),  # Green for the green center
            'b': (0, 0, 255)  # Blue for the blue center
        }

        for color, center in centers.items():
            center_x = center['x']
            center_y = center['y']

            # Draw the X by drawing two diagonal lines
            size = 10  # Increase the size of the X marks

            pygame.draw.line(screen, colors[color], (center_x - size, center_y - size),
                             (center_x + size, center_y + size), 2)  # Top-left to bottom-right
            pygame.draw.line(screen, colors[color], (center_x - size, center_y + size),
                             (center_x + size, center_y - size), 2)  # Bottom-left to top-right
