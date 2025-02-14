import math
from constants import *


def normalize_vector(dx, dy):
    # Use sqrt(x²+y²) directly instead of hypot if maximum precision isn't needed
    magnitude = (dx * dx + dy * dy) ** 0.5
    if magnitude:
        inv_mag = 1.0 / magnitude  # Calculate inverse once
        return dx * inv_mag, dy * inv_mag
    return 0, 0


def adjust_vector_closer(star, near_star, adjust_rate):
    # Cache square root calculation
    current_speed = (star.dx * star.dx + star.dy * star.dy) ** 0.5

    # Combine calculations to reduce operations
    new_dx = star.dx + (near_star.dx - star.dx) * adjust_rate
    new_dy = star.dy + (near_star.dy - star.dy) * adjust_rate

    # Use the optimized normalize_vector function
    magnitude = (new_dx * new_dx + new_dy * new_dy) ** 0.5
    if magnitude:
        inv_mag = current_speed / magnitude
        star.dx = new_dx * inv_mag
        star.dy = new_dy * inv_mag


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
    corner_margin = 400
    max_corner_force = 0.4

    # Cache position values
    pos_x, pos_y = star.pos_x, star.pos_y

    # Basic edge avoidance - use early returns to avoid unnecessary checks
    if pos_x < edge_threshold:
        star.dx += steer_strength
    elif pos_x > WINDOW_WIDTH - edge_threshold:
        star.dx -= steer_strength

    if pos_y < edge_threshold:
        star.dy += steer_strength
    elif pos_y > WINDOW_HEIGHT - edge_threshold:
        star.dy -= steer_strength

    # Optimize corner checks by combining conditions
    is_left = pos_x < corner_margin
    is_right = pos_x > WINDOW_WIDTH - corner_margin
    is_top = pos_y < corner_margin
    is_bottom = pos_y > WINDOW_HEIGHT - corner_margin

    if (is_left or is_right) and (is_top or is_bottom):
        # Calculate corner distances only when necessary
        if is_left and is_top:
            dist = (pos_x * pos_x + pos_y * pos_y) ** 0.5
        elif is_right and is_top:
            dx = WINDOW_WIDTH - pos_x
            dist = (dx * dx + pos_y * pos_y) ** 0.5
        elif is_left and is_bottom:
            dy = WINDOW_HEIGHT - pos_y
            dist = (pos_x * pos_x + dy * dy) ** 0.5
        else:  # right and bottom
            dx = WINDOW_WIDTH - pos_x
            dy = WINDOW_HEIGHT - pos_y
            dist = (dx * dx + dy * dy) ** 0.5

        if dist < corner_margin:
            force = max_corner_force * (1 - dist / corner_margin)
            if is_left:
                star.dx += force
            else:
                star.dx -= force
            if is_top:
                star.dy += force
            else:
                star.dy -= force

    # Normalize only when necessary
    dx, dy = star.dx, star.dy
    mag_sq = dx * dx + dy * dy
    if mag_sq > 1.0:  # Only normalize if magnitude > 1
        mag = mag_sq ** 0.5
        star.dx = dx / mag
        star.dy = dy / mag


def apply_cohesion(star, nearby_stars, mod_cohesion_strength):
    cohesion_distance_sq = 10000  # Pre-compute 100²

    # Cache star's attributes
    sx, sy = star.pos_x, star.pos_y
    gene = star.gene_preference

    # Pre-allocate sums instead of using center coordinates
    sum_x = 0
    sum_y = 0
    num_neighbors = 0

    for other_star in nearby_stars:
        if other_star is star:
            continue

        if other_star.gene_preference != gene:
            continue

        dx = other_star.pos_x - sx
        dy = other_star.pos_y - sy

        if dx * dx + dy * dy <= cohesion_distance_sq:
            sum_x += other_star.pos_x
            sum_y += other_star.pos_y
            num_neighbors += 1

    if num_neighbors:
        inv_num = 1.0 / num_neighbors
        center_x = sum_x * inv_num
        center_y = sum_y * inv_num

        to_center_x = center_x - sx
        to_center_y = center_y - sy

        # Combine normalization with force application
        dist_sq = to_center_x * to_center_x + to_center_y * to_center_y
        if dist_sq > 0:
            dist = dist_sq ** 0.5
            force = mod_cohesion_strength / dist
            star.dx += to_center_x * force
            star.dy += to_center_y * force

            # Only normalize if necessary
            dx, dy = star.dx, star.dy
            mag_sq = dx * dx + dy * dy
            if mag_sq > 1.0:
                mag = mag_sq ** 0.5
                star.dx = dx / mag
                star.dy = dy / mag

    return num_neighbors > 0
