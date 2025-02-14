import math


class Star:
    def __init__(self, pos_x=None, pos_y=None, dx=None, dy=None, velocity=None, color=None, lifespan=None,
                 prefered_gene=None, solitude_tolerance=None):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dx = dx
        self.dy = dy
        self.velocity = velocity
        self.color = color
        self.size = 10
        self.lifetime = 0
        self.lifespan = lifespan
        self.gene_preference = prefered_gene
        self.health_points = 200
        self.solitude_tolerance = solitude_tolerance
        self.time_alone = 0
        self.normalize_needed = False


