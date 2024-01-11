from enum import Enum
import random
import heapq


class Facing(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

    def __neg__(self):
        if self == Facing.NORTH:
            return Facing.SOUTH
        elif self == Facing.SOUTH:
            return Facing.NORTH
        elif self == Facing.EAST:
            return Facing.WEST
        else:
            return Facing.EAST

    def __add__(self, other):
        if type(other) == Facing:
            return self.value[0] + other.value[0], self.value[1] + other.value[1]
        else:
            return self.value[0] + other[0], self.value[1] + other[1]


def manhattan_distance(p1, p2):
    return sum(abs(p1[i] - p2[i]) for i in range(len(p1)))


def manhattan_neighbors(p):
    return [(p[0] + f.value[0], p[1] + f.value[1]) for f in Facing]


def within(p, width, height):
    return 0 <= p[0] < width and 0 <= p[1] < height


def projection(obstacles, width, height, at, facing):
    if (at, facing) not in obstacles:
        future = facing + at
        if within(future, width, height):
            return future


def generate_grid_obstacles(width, height, num_obstacles):
    obstacles = set()
    obstacle_facings = [Facing.SOUTH, Facing.EAST]
    obstacle_candidates = [(x, y, f) for x in range(width - 1) for y in range(height - 1) for f in obstacle_facings]
    random.shuffle(obstacle_candidates)
    obstacle_candidate = 0
    while len(obstacles) < num_obstacles and obstacle_candidate < len(obstacle_candidates):
        x1, y1, f = obstacle_candidates[obstacle_candidate]
        obstacles.add(((x1, y1), f))
        x2, y2 = f + (x1, y1)
        obstacles.add(((x2, y2), -f))
        obstacle_candidate += 1
        if not all_cells_reachable(obstacles, width, height):
            obstacles.remove(((x1, y1), f))
            obstacles.remove(((x2, y2), -f))
    return obstacles


def all_cells_reachable(obstacles, width, height):
    reached = set()
    heap = [(0, (0, 0))]
    while len(heap) > 0:
        cost, current = heapq.heappop(heap)
        if current not in reached:
            reached.add(current)
            for f in Facing:
                neighbor = f + current
                if within(neighbor, width, height) and (neighbor, f) not in obstacles:
                    heapq.heappush(heap, (1 + cost, neighbor))
    return len(reached) == width * height


def show_grid(obstacles, width, height):
    print(" ", end='')
    for x in range(width):
        print(f" {x}", end='')
    print()
    for y in range(height):
        if y > 0:
            print("  ", end='')
            for x in range(width):
                if ((x, y), Facing.NORTH) in obstacles:
                    print("_ ", end='')
                else:
                    print(". ", end='')
            print()
        print(f"{y} ", end='')
        for x in range(width):
            if x > 0:
                if ((x, y), Facing.WEST) in obstacles:
                    print("|", end='')
                else:
                    print(".", end='')
            print("O", end='')
        print()


def a_star(obstacles, width, height, start, end):
    visited = {}
    frontier = [(0, manhattan_distance(start, end), start, None)]
    current = None
    while len(frontier) > 0:
        if current == end:
            path = []
            while current is not None:
                path = [current] + path
                current = visited[current]
            return path
        else:
            cost, estimate, current, parent = heapq.heappop(frontier)
            if current not in visited:
                visited[current] = parent
                for f in Facing:
                    n = f + current
                    if within(n, width, height) and (current, f) not in obstacles:
                        heapq.heappush(frontier, (cost + 1, manhattan_distance(n, end), n, current))
