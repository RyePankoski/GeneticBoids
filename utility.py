import math
from constants import *


def normalize_vector(dx, dy):
    magnitude = math.hypot(dx, dy)
    if magnitude:
        return dx / magnitude, dy / magnitude
    return 0, 0


def adjust_vector_closer(star, near_star, adjust_rate):
    current_speed = math.sqrt(star.dx * star.dx + star.dy * star.dy)

    # Calculate direction adjustment
    new_dx = star.dx + (near_star.dx - star.dx) * adjust_rate
    new_dy = star.dy + (near_star.dy - star.dy) * adjust_rate

    # Normalize and restore original speed
    normalized_dx, normalized_dy = normalize_vector(new_dx, new_dy)
    star.dx = normalized_dx * current_speed
    star.dy = normalized_dy * current_speed


def repel_diff_genes(star, near_star, repel_rate):
    current_speed = math.sqrt(star.dx * star.dx + star.dy * star.dy)

    # Calculate repulsion vector (opposite to the direction to neighbor)
    repel_dx = star.pos_x - near_star.pos_x
    repel_dy = star.pos_y - near_star.pos_y

    # Normalize repulsion vector
    repel_dx, repel_dy = normalize_vector(repel_dx, repel_dy)

    # Apply repulsion while maintaining speed
    new_dx = star.dx + repel_dx * repel_rate
    new_dy = star.dy + repel_dy * repel_rate

    # Normalize and restore original speed
    normalized_dx, normalized_dy = normalize_vector(new_dx, new_dy)
    star.dx = normalized_dx * current_speed
    star.dy = normalized_dy * current_speed
    star.normalize_needed = True


def adjust_vector_farther(star, near_star, adjust_rate):
    current_speed = math.sqrt(star.dx * star.dx + star.dy * star.dy)

    # Calculate repulsion vector (opposite to the direction to neighbor)
    repel_dx = star.pos_x - near_star.pos_x
    repel_dy = star.pos_y - near_star.pos_y

    # Normalize repulsion vector
    repel_dx, repel_dy = normalize_vector(repel_dx, repel_dy)

    # Apply repulsion while maintaining speed
    new_dx = star.dx + repel_dx * adjust_rate
    new_dy = star.dy + repel_dy * adjust_rate

    # Normalize and restore original speed
    normalized_dx, normalized_dy = normalize_vector(new_dx, new_dy)
    star.dx = normalized_dx * current_speed
    star.dy = normalized_dy * current_speed


def handle_boundaries(star):
    edge_threshold = 100
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

    # Corner avoidance: only compute distance if the star is near a corner.
    corner_margin = 400
    max_corner_force = 0.4

    # Top-left corner
    if star.pos_x < corner_margin and star.pos_y < corner_margin:
        dist = math.hypot(star.pos_x, star.pos_y)
        if dist < corner_margin:
            force = max_corner_force * (1 - dist / corner_margin)
            star.dx += force
            star.dy += force

    # Top-right corner
    elif star.pos_x > WINDOW_WIDTH - corner_margin and star.pos_y < corner_margin:
        dist = math.hypot(WINDOW_WIDTH - star.pos_x, star.pos_y)
        if dist < corner_margin:
            force = max_corner_force * (1 - dist / corner_margin)
            star.dx -= force
            star.dy += force

    # Bottom-left corner
    elif star.pos_x < corner_margin and star.pos_y > WINDOW_HEIGHT - corner_margin:
        dist = math.hypot(star.pos_x, WINDOW_HEIGHT - star.pos_y)
        if dist < corner_margin:
            force = max_corner_force * (1 - dist / corner_margin)
            star.dx += force
            star.dy -= force

    # Bottom-right corner
    elif star.pos_x > WINDOW_WIDTH - corner_margin and star.pos_y > WINDOW_HEIGHT - corner_margin:
        dist = math.hypot(WINDOW_WIDTH - star.pos_x, WINDOW_HEIGHT - star.pos_y)
        if dist < corner_margin:
            force = max_corner_force * (1 - dist / corner_margin)
            star.dx -= force
            star.dy -= force

    # Normalize final velocity
    mag = math.hypot(star.dx, star.dy)
    if mag:
        star.dx /= mag
        star.dy /= mag


def apply_cohesion(star, nearby_stars, mod_cohesion_strength):
    cohesion_distance = 100
    cohesion_distance_sq = cohesion_distance * cohesion_distance
    cohesion_strength = mod_cohesion_strength

    center_x = 0
    center_y = 0
    num_neighbors = 0

    # Cache star's attributes for faster access
    sx = star.pos_x
    sy = star.pos_y
    gene = star.gene_preference

    for other_star in nearby_stars:
        if other_star is star:
            continue

        dx = other_star.pos_x - sx
        dy = other_star.pos_y - sy

        # Use the precomputed squared distance
        if dx * dx + dy * dy > cohesion_distance_sq:
            continue

        if gene == other_star.gene_preference:
            center_x += other_star.pos_x
            center_y += other_star.pos_y
            num_neighbors += 1

    if num_neighbors:
        center_x /= num_neighbors
        center_y /= num_neighbors

        # Direction to the center of mass
        to_center_x = center_x - sx
        to_center_y = center_y - sy
        distance = math.hypot(to_center_x, to_center_y)
        if distance:
            to_center_x /= distance
            to_center_y /= distance

            # Apply cohesion force
            star.dx += to_center_x * cohesion_strength
            star.dy += to_center_y * cohesion_strength

            # Normalize final velocity
            mag = math.hypot(star.dx, star.dy)
            if mag:
                star.dx /= mag
                star.dy /= mag

    return num_neighbors > 0
