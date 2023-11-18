# Barebones class for Conway's Game of Life
# No need to add complexity to optimize for streaming updates or only getting changed updates bc Nanoleaf requires states for all the panels for any update anyways
class ConwaysGameOfLife:
    def __init__(self, x_size, y_size):
        self.x_size = x_size
        self.y_size = y_size
        self._state = [[False for _ in range(self.y_size)] for _ in range(self.x_size)]
    
    def set(self, x, y, val=True):
        if 0 <= x < self.x_size and 0 <= y < self.y_size:
            self._state[x][y] = val
        else:
            raise Exception(f'Attempted to set state for out-of-bounds coords: {x}, {y}')
    
    def batch_set(self, coords=[], val=True):
        for x, y in coords:
            self.set(x, y, val)
        
    def count_neighbors(self, x, y):
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                if 0 <= x + dx < self.x_size and 0 <= y + dy < self.y_size:
                    count += self._state[x + dx][y + dy]
        return count

    def will_live(self, x, y):
        neighbors = self.count_neighbors(x, y)
        if self._state[x][y]:
            return 2 <= neighbors <= 3
        else:
            return neighbors == 3

    def dump_state(self):
        for x in range(self.x_size):
            for y in range(self.y_size):
                yield (x, y, self._state[x][y])

    def tick(self):
        updates = []
        for x in range(self.x_size):
            for y in range(self.y_size):
                will_live = self.will_live(x, y)
                if self._state[x][y] != will_live:
                    updates.append((x, y, will_live))
        for x, y, val in updates:
            self._state[x][y] = val
