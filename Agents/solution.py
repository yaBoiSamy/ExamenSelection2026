"""
Robot Rescue Challenge - Solution Template

Implement your solution in the `solve` function below.
Your goal is to rescue the person trapped in the building as quickly as possible.

Available Robot methods:
    - robot.move(Direction) -> bool: Move in a direction (FORWARD, BACKWARD, LEFT, RIGHT)
    - robot.sense_fires_around() -> int: Get count of fires in adjacent cells (only cardinal directions, no diagonals) (does not cost time)
    - robot.scan_fires() -> Set[Position]: Get fire positions in cells around the robot (costs 10 seconds)
    - robot.position -> Position: Current robot position
    - robot.is_carrying_person -> bool: Whether robot is carrying someone
    - robot.get_grid_dimensions() -> Tuple[int, int]: Get (width, height)
    - robot.get_exit_position() -> Position: Get exit position
    - robot.get_person_position() -> Position: Get the person's position (known location)

Movement costs:
    - Each move: 1 second
    - Scan: 10 seconds

Rules:
    - There is exactly one person to rescue
    - The person's location is known from the start
    - Stepping on fire destroys the robot (mission fails immediately)
    - Robot starts at the exit position
    - Person is picked up automatically when robot reaches their cell
    - Mission ends automatically when robot returns to exit with the person

Objective: Navigate to the person, pick them up, and return to the exit as quickly as possible!
"""

from robot import Robot, Direction, Position
from enum import Enum
from collections import deque


def solve(robot: Robot) -> None:
    def tup_to_complex(tup):
        return complex(tup[0], tup[1])

    def adjust_pos(tup_pos):
        border_pos_adjustment = complex(1, 1)  # To account for border padding
        tup_to_complex(tup_pos) + border_pos_adjustment

    def robot_pos():
        adjust_pos(robot.position)

    border_pos_adjustment = complex(1, 1)  # To account for border padding
    width, height = robot.get_grid_dimensions()
    exit_pos = adjust_pos(robot.get_exit_position())
    person_pos = adjust_pos(robot.get_person_position())
    grid = Grid(width, height, exit_pos, person_pos)

    destination = person_pos
    while(True):
        grid.get_tile(robot_pos()).explore(robot.sense_fires_around())
        grid.best_direction(robot_pos(), destination)
        grid.  # J'ai pas eu le temps de finir :(



def dir_to_complex(direction):
    match direction:
        case Direction.FORWARD:
            return 0 - 1j
        case Direction.BACKWARD:
            return 0 + 1j
        case Direction.LEFT:
            return -1 + 0j
        case Direction.RIGHT:
            return 1 + 0j

class Grid:
    class Tile:
        class TileState(Enum):
            UNKOWN = 0
            EXPLORED = 1
            FIRE = 2
            EMPTY = 3
            DEAD_END = 4
            PERSON = 5

        def __init__(self, position, state, get_neighbour):
            self.state = state
            self.neighbouring_fires = -1
            self.position = position
            self.get_neighbour = get_neighbour

        def explore(self, neighbouring_fires):
            self.state = self.TileState.EXPLORED
            self.neighbouring_fires = neighbouring_fires
            self.propagate_inference()

        def get_neighbours(self):
            top = self.get_neighbour(self.position, Direction.FORWARD)
            bottom = self.get_neighbour(self.position, Direction.BACKWARD)
            left = self.get_neighbour(self.position, Direction.LEFT)
            right = self.get_neighbour(self.position, Direction.RIGHT)
            return { top, bottom, left, right }

        def is_safe(self):
            return self.state == self.TileState.EXPLORED or self.state == self.TileState.EMPTY
        
        def is_inaccessible(self):
            return self.state == self.TileState.FIRE or self.state == self.TileState.DEAD_END
        
        def propagate_inference(self, neighbours):
            for neighbour in neighbours:
                neighbour.infer()
        
        def declare_empty(self, unknown_neighbours):
            for neighbour in unknown_neighbours:
                neighbour.state = self.TileState.EMPTY
                neighbour.propagate_inference()
        
        def declare_fire(self, unknown_neighbours):
            for neighbour in unknown_neighbours:
                neighbour.state = self.TileState.FIRE
                neighbour.propagate_inference()

        def infer(self):
            if (self.state == self.TileState.UNKOWN or \
                self.state == self.TileState.PERSON or \
                self.state == self.TileState.FIRE   or \
                self.state == self.TileState.DEAD_END):
                return # inference completed or impossible, waste of compute
            
            neighbours = self.get_neighbours()
            unknown_neighbours = { neighbour for neighbour in neighbours if neighbour.state == self.TileState.UNKOWN }
            fire_neighbours = { neighbour for neighbour in neighbours if neighbour.state == self.TileState.FIRE }
            inaccessible_neighbours = { neighbour for neighbour in neighbours if neighbour.is_inaccessible() }

            if (self.state == self.TileState.EXPLORED):
                if (len(fire_neighbours) == self.neighbouring_fires):
                    self.declare_empty(unknown_neighbours)
                elif (self.neighbouring_fires - len(fire_neighbours) == len(unknown_neighbours)):
                    self.declare_fire(unknown_neighbours)

            if self.is_safe() and len(inaccessible_neighbours) > 2:
                self.state = self.TileState.DEAD_END
                self.propagate_inference()
                

    def __init__(self, width, height, exit_pos, person_pos):
        def init_state(x, y):
            pos = complex(x, y)
            if pos == person_pos:
                return self.Tile.TileState.PERSON
            if pos == exit_pos:
                return self.Tile.TileState.EMPTY
            if x == 0 or y == 0 or x == width + 1 or y == height + 1:
                return self.Tile.TileState.FIRE # Border padding
            return self.Tile.TileState.UNKOWN
        
        self.contents = [[self.Tile(complex(x, y), init_state(x, y), self.get_neighbour) \
                          for x in range(width + 2)] for y in range(height + 2)]
        self.width = width + 2
        self.height = height + 2
        
    def get_tile(self, position):
        return self.contents[position.imag()][position.real()]

    def get_neighbour(self, position, direction):
        neighbour_pos = position + dir_to_complex(direction)
        return self.get_tile(neighbour_pos)
    
    def best_direction(self, src, dst):  # bfs
        directions = { Direction.FORWARD, Direction.BACKWARD, Direction.LEFT, Direction.RIGHT }
        q = deque()
        q.append(self.get_tile(dst))
        distance = [[-1 for _ in range(self.width)] for _ in range(self.height)]
        def get_dist(pos):
            return distance[pos.imag()][pos.real()]
        def set_dist(pos, dist):
            distance[pos.imag()][pos.real()] = dist 
        set_dist(dst, 0)
        while q:
            pos = q.popleft()
            for direction in directions:
                adj_pos = pos + dir_to_complex(direction)
                if get_dist(adj_pos) == -1:
                    adj_tile = self.get_tile(adj_pos)
                    if adj_tile.is_safe() or adj_tile.state == self.Tile.TileState.UNKOWN:  # greedily assume unkown tiles are safe
                        set_dist(adj_pos, get_dist(adj_pos) + 1)
                        q.append(adj_tile)
        adj_tiles = self.get_tile(src).get_neighbours()
        minTile = None
        for tile in adj_tiles:
            if minTile is None or get_dist(tile.position) < get_dist(minTile.position):
                minTile = tile
        return minTile

        