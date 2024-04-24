import numpy as np
from src.utils import Stone

class Board(np.ndarray):
    '''
    Instance of a 2D grid board extended from np.ndarray
    '''
    def __new__(cls, config={}):
        '''
        Standard procedure for subclassing np.ndarray
        '''
        # dimension of the board
        board_size = config['board_size']
        shape = (board_size, board_size)
        obj = super(Board, cls).__new__(cls, shape, dtype=np.int_)

        obj.board_size = board_size

        # string to display as a black stone
        obj.black_stone_render = config['black_stone']

        # string to display as a white stone
        obj.white_stone_render = config['white_stone']

        # fill board with empty slots
        obj.fill(Stone.EMPTY)

        return obj

    def __array_finalize__(self, obj):
        '''
        Standard procedure for subclassing np.ndarray
        '''
        if obj is None:
            return
        self.board_size = getattr(obj, 'board_size')
        self.black_stone_render = getattr(obj, 'black_stone_render')
        self.white_stone_render = getattr(obj, 'white_stone_render')

    def get_liberty_coords(self, y, x):
        '''
        Return the liberty coordinates for (y, x). This constitutes
        "up", "down", "left", "right" if possible.
        '''
        coords = []
        if y > 0:
            coords.append((y-1, x))
        if y < self.board_size-1:
            coords.append((y+1, x))
        if x > 0:
            coords.append((y, x-1))
        if x < self.board_size-1:
            coords.append((y, x+1))
        return coords

    #def place_stone(self, stone, y, x):
        '''
        Place a stone at the specified coordinate
        '''
        self[y][x] = stone
        
    def place_stone(self, stone, y, x):
    # Check if the position is within the board boundaries
        if 0 <= y < self.board_size and 0 <= x < self.board_size:
        # Check if the position is already occupied
            if self[y][x] != Stone.EMPTY:
                raise Exception("Position already occupied")
            else:
                self[y][x] = stone
        else:
            raise Exception("Invalid position")


    def remove_stone(self, y, x):
        '''
        Remove the stone at the specified coordinate
        '''
        self[y][x] = Stone.EMPTY

    def is_within_bounds(self, y, x):
        '''
        Check if the given coordinate is within bounds of the board
        '''
        return 0 <= y <= self.board_size and 0 <= x <= self.board_size

    def _value_to_render(self, stone):
        '''
        Map from the stone to the displayed string for that stone
        '''
        s = None
        if stone == Stone.EMPTY:
            s = ' '
        elif stone == Stone.BLACK:
            s = self.black_stone_render
        elif stone == Stone.WHITE:
            s = self.white_stone_render
        return f'[{s}]'

    def _render(self):
        '''
        Render the board, with axes labelled from 0, 1, 2, ..., 9, A, B, ...
        and so on
        '''
        # horizontal axis
        print('\n   ' + '  '.join([self._index_to_label(x) \
                            for x in range(self.board_size)]))

        # vertical axis is printed with each row
        for row in range(self.board_size):
            label = self._index_to_label(row)
            board_row = map(self._value_to_render, self[row])
            print(f'{label} ' + ''.join(board_row))

        print('')

    def _index_to_label(self, idx):
        '''
        Map the index to displayed axis coordinate
        Eg. _index_to_label(3) --> '3'
            _index_to_label(13) --> 'D'
        '''
        if idx < 10:
            return str(idx)
        return chr(idx - 10 + ord('A'))
    
    def get_legal_actions(self, stone):
        '''
        Get the legal actions (valid moves) for a given stone color.
        '''
        legal_actions = []
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self._is_legal_move(stone, y, x):
                    legal_actions.append((y, x))
        return legal_actions

    
       # Inside the Board class in board.py
    def _is_legal_move(self, stone, y, x):
        '''
        Check if placing a stone at (y, x) is a legal move.
        A move is legal if it would result in capturing opponent stones.
        '''
        # Check if the position is within the board boundaries
        if not self.is_within_bounds(y, x) or self[y][x] != Stone.EMPTY:
            return False
        
        return True
        # Check if the position is already occupied
        #if self[y][x] != Stone.EMPTY:
           # return False

        # Check if placing a stone at (y, x) would capture opponent stones
        captured_stones = []
        for ly, lx in self.get_liberty_coords(y, x):
            if self[ly][lx] != stone and self._group_is_captured(ly, lx):
                captured_stones.append((ly, lx))

        return bool(captured_stones)

    def _group_is_captured(self, y, x):
        
        stone = self[y][x]
        visited = set()
        queue = [(y, x)]

        while queue:
            cy, cx = queue.pop()
            if (cy, cx) in visited:
                continue
            visited.add((cy, cx))

            for ny, nx in self.get_liberty_coords(cy, cx):
                if self[ny][nx] == Stone.EMPTY:
                    return False
                elif self[ny][nx] == stone and (ny, nx) not in visited:
                    queue.append((ny, nx))

        return True

   