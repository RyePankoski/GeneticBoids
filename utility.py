import math
from constants import *


def normalize_vector(dx, dy):
    magnitude = math.sqrt(dx * dx + dy * dy)
    if magnitude != 0:
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


def apply_cohesion(star, nearby_stars, mod_cohesion_strength):
    cohesion_distance = 100
    cohesion_strength = mod_cohesion_strength

    # Initialize variables for cohesion
    center_x = 0
    center_y = 0
    num_neighbors = 0

    # Calculate center of mass for genetically compatible neighbors
    for other_star in nearby_stars:
        if other_star is star:
            continue

        dx = other_star.pos_x - star.pos_x
        dy = other_star.pos_y - star.pos_y
        distance_sq = dx * dx + dy * dy

        if distance_sq > cohesion_distance * cohesion_distance:
            continue

        if star.gene_preference == other_star.gene_preference:
            center_x += other_star.pos_x
            center_y += other_star.pos_y
            num_neighbors += 1

    # Apply cohesion force if we have neighbors
    if num_neighbors > 0:
        # Calculate center of mass
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

    return num_neighbors > 0
