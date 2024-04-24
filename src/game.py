from src.board import Board
from src.utils import Stone, make_2d_array
from src.group import Group, GroupManager
from src.exceptions import (
    SelfDestructException, KoException, InvalidInputException)
import random


class Agent:
    """Abstract stateless agent."""
    def __init__(self, color):
        """
        :param color: 'BLACK' or 'WHITE'
        """
        self.color = color

    @classmethod
    def terminal_test(cls, board):
        return board.winner is not None

    def get_action(self, board: Board):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__ + '; color: ' + self.color

class RandomAgent(Agent):
    """Pick a random action."""
    def __init__(self, color):
        super().__init__(color)

    def get_action(self, board):
        actions = board.get_legal_actions(self.color)
        return random.choice(actions) if actions else None


class Game(object):
    '''
    Manage the high level gameplay of Go
    '''
    def __init__(self, config):

        # 2D board
        self.board = Board(config)

        # dimension of the square board
        self.board_size = config['board_size']

        # group manager instance
        self.gm = GroupManager(self.board,
                               enable_self_destruct=config['enable_self_destruct'])
        
        # count the number of consecutive passes
        self.count_pass = 0
        self.is_game_over = False  # This attribute to manage game over state
        
    def _end_game(self):
        self.is_game_over = True
        
    def place_black(self, y, x):
        '''
        Place a black stone at coordinate (y, x)
        '''
        self._place_stone(Stone.BLACK, y, x)

    def place_white(self, y, x):
        '''
        Place a white stone at coordinate (y, x)
        '''
        self._place_stone(Stone.WHITE, y, x)

    def pass_turn(self):
        '''
        Pass this turn
        '''
        self.count_pass += 1

    def is_over(self):
        return self.is_game_over
        '''
        Check if the game is over (only if there are two consecutive passes)
        '''
        # return self.count_pass >= 2
        if self.count_pass >= 2:
            return True

        # Check for any moves left on the board
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y, x] == Stone.EMPTY:
                    return False

        return True
    
    def is_within_bounds(self, y, x):
        '''
        Check if the given coordinate is within the range of the board
        '''
        return self.board.is_within_bounds(y, x)

    def _place_stone(self, stone, y, x):
        '''
        Place a stone at (y, x), then resolve interactions due to the move.
        Throw an exception if self-destruct or ko rules are violated
        '''
        if stone == Stone.EMPTY:
            return
        self.board.place_stone(stone, y, x)

        try:
            self.gm.resolve_board(y, x)
        except SelfDestructException as e:
            self.board.remove_stone(y, x)
            raise e
        except KoException as e:
            self.board.remove_stone(y, x)
            raise e
            
        self.count_pass = 0
        self.gm.update_state()

    @property
    def num_black_captured(self):
        '''
        Return the number of captured black stones
        '''
        return self.gm._num_captured_stones[Stone.BLACK]

    @property
    def num_white_captured(self):
        '''
        Return the number of captured white stones
        '''
        return self.gm._num_captured_stones[Stone.WHITE]

    def render_board(self):
        '''
        Render the board
        '''
        self.board._render()

    def get_scores(self):
        '''
        Return the score of black and white.
        Scoring is counted based on territorial rules, with no interpolation of dead/alive groups.
        An area is a territory for a player if any area within that territory can only reach
        stones of of that player.
        '''
        scores = {Stone.BLACK: 0,
                  Stone.WHITE: 0
                 }
        traversed = make_2d_array(self.board_size, self.board_size,
                                  default=lambda: False)
        #return scores

        def traverse(y, x):
            traversed[y][x] = True
            search = [(y, x)]
            stone = None
            count = 1
            is_neutral = False

            while search:
                y, x = search.pop()
                for ly, lx in self.board.get_liberty_coords(y, x):
                    this_stone = self.board[ly, lx]
                    if this_stone != Stone.EMPTY:
                        stone = stone or this_stone
                        if stone != this_stone:
                            is_neutral = True                
                    if not traversed[ly][lx]:
                        if this_stone == Stone.EMPTY:
                            count += 1
                            search.append((ly, lx))
                    traversed[ly][lx] = True

            if is_neutral:
                return 0, Stone.EMPTY
            return count, stone

        for y in range(self.board_size):
            for x in range(self.board_size):
                if not traversed[y][x] and self.board[y, x] == Stone.EMPTY:
                    score, stone = traverse(y, x)
                    if stone is not None and stone != Stone.EMPTY:
                        scores[stone] += score

        scores[Stone.BLACK] -= self.num_black_captured
        scores[Stone.WHITE] -= self.num_white_captured
        return scores


class GameUI(object):
    '''
    Main interface between the game and the players
    '''
    def __init__(self, config):
        # the game object
        self.game = Game(config)
        # store which player's turn it is
        self.turn = None
        self.ai = None

    def play(self):
        #print("Starting game...")
        while not self.game.is_game_over:  # Use is_game_over from the Game class
            self.game.render_board()
            
            if self.turn == Stone.BLACK:
                move = self._prompt_move()
            elif self.ai:
                move = self._get_ai_move()
            else:
                print("Error: No valid player or AI set.")
                break

            if move == 'pass':
                self.game.pass_turn()
            elif move == 'quit':
                self.game._end_game()  # End the game 
                self._display_result()               
                break
            else:
                self._place_stone(move)

            self._switch_turns()
            
        #if not self.game.is_game_over and move != 'quit':
            #print("The game is not over yet 88888.")
       # else:                
          #  self._display_result()
        
    def _get_ai_move(self):
        move = self.ai.get_action(self.game.board)
        if move is None:
            return 'pass'
        return move
    
    def _display_result(self):
        '''
        Show the result of the game including the scores and winner
       
        '''
        #if self.game.is_over():
        scores = self.game.get_scores()
        black_score = scores[Stone.BLACK]
        white_score = scores[Stone.WHITE]

        print(f'Black score: {Stone.BLACK}')
        print(f'White score: {Stone.WHITE}')

        #if black_score == white_score:
            #print('The result is a tie!')
            
        #else:
        winner = Stone.BLACK if black_score > white_score else Stone.WHITE
        winner = self._get_player_name(winner)
        print(f'The winner is {winner}!')      
              
        #elif:
                #scores = self.game.get_scores()
                #black_score = scores[Stone.BLACK]
                #white_score = scores[Stone.WHITE]

                #print(f'Black score: {black_score}')
                #print(f'White score: {white_score}')
                #print("The game is not over yet.")
                
    def _place_stone(self, move):
        '''
        Place a stone at the specified coordinate. Return True if it is valid
        '''
        if move == 'pass':
            self.game.pass_turn()
            print(f'{self._get_player_name(self.turn)} passed.')
            return
        elif move == 'quit':
            self.game.is_game_over = True
            print(f'{self._get_player_name(self.turn)} quit the game.')
            return
        
        y, x = move
        try:
            if self.turn == Stone.BLACK:
                self.game.place_black(y, x)
            elif self.turn == Stone.WHITE:
                self.game.place_white(y, x)
           # is_turn_over = True
            self.game.count_pass = 0  # Reset pass counter on a valid move
            print(f'{self._get_player_name(self.turn)} placed a stone at ({y}, {x}).')
        except Exception as e:
            print(e)
           # is_turn_over = False
       # return is_turn_over

    def _get_player_name(self, stone):
        '''
        Return the player name for the specified stone
        '''
        return 'Black' if stone == Stone.BLACK else 'White'

    def _switch_turns(self):
        '''
        Swap the turn
        '''
        self.turn = Stone.BLACK if self.turn == Stone.WHITE else Stone.WHITE
        
    def _prompt_move(self):
        '''
        Prompt a user input move. The input format is one of
            - "pass" to pass for the current player   or
            - "y x" to place a stone at the specified coordinate
        The prompt repeats until a valid input is given
        '''
        move = None
        player = self._get_player_name(self.turn)
        while not self._is_valid_input(move):
            print('Please input a valid move' 
            '(enter "pass"/"quit" to pass/quit or "y x" to place a stone at the coordinate (y, x))')
            move = input(f'{player} move: ').upper()
        
            if move.lower() == 'quit':
                self.game.is_game_over = True  # Set the game over flag
                return 'quit'
            
        return self._parse_move(move)
    
    def _is_valid_input(self, move):
        '''
        Check if the given input would give a valid move, in terms of placing a stone
        on the board
        '''
        if move == 'pass':
            return True
        try:
            y, x = self._parse_coordinates(move)
            return self.game.is_within_bounds(y, x)
        except:
            return False

    def _parse_coordinates(self, move):
        '''
        Parse the coordinate input into (y, x) valid coordinates
        '''
        y, x = move.strip().split()
        y = self._label_to_coord(y)
        x = self._label_to_coord(x)
        return y, x
    
    def _label_to_coord(self, label):
        '''
        Translate an individual input coordinate into a valid one.
        The labels are given as 0, 1, 2, ... , 9, A, B, ...
        This helper translates all labels into integer coordinates
        Eg. _label_to_coord('9') --> 9
            _label_to_coord('A') --> 10
            _label_to_coord('C') --> 12
        '''
        if label.isnumeric():
            coord = int(label)
            if coord >= 10:
                raise InvalidInputException
            return int(label)
        if label.isalpha() and label >= 'A':
            diff = ord(label) - ord('A')
            if diff < 0:
                raise InvalidInputException
            return 10 + diff
        raise InvalidInputException

    def _parse_move(self, move):
        '''
        Parse an arbitrary input
        '''
        if move == 'pass':
            return move
        return self._parse_coordinates(move)

class GoGame:
    def __init__(self, config):
        self.config = config
        self.is_game_over = False
        self.count_pass = 0  # Initialize the pass counter
        
    def play(self):
       # print("Starting game...")
        while not self.is_over():
            self.render_board()
            command = input(f"{self._get_player_name(self.turn)} move: ")

            if self.handle_command(command):  # if command returns True, break the loop
                 break

                # Continue with other game moves if not quitting
                # ...

            self._display_result()
            pass

            if self.turn == Stone.BLACK:
                move = self._prompt_move()
            else:
                move = self._get_ai_move()

            if move == 'pass':
                self.pass_turn()
            elif move == 'quit':
                self.game._end_game()  # End the game
                self._display_result()
                break
            else:
                self._place_stone(move)
                self.count_pass = 0  # Reset pass counter on a valid move

            self._switch_turns()

            self._display_result()

    def _get_ai_move(self):
        move = self.ai.get_action(self.game.board)
        if move is None:
            return 'pass'
        return move

    def pass_turn(self):
        self.count_pass += 1
        if self.count_pass >= 2:  # If both players pass consecutively, end the game
            self._end_game()

    def _end_game(self):
        self.is_game_over = True
        print("Game marked as over.")
        
    def is_over(self):
        return self.is_game_over
        #return self.count_pass >= 2 or self.some_other_end_condition

    def handle_command(self, command):
        if command.strip().lower() == 'quit':
            self.game.end_game()  # Ensures the game is marked as over
            return True  # Indicates a command to quit was handled
        # Handle other commands
    
    def get_scores(self):
    # Your score calculation logic goes here
    # This needs to handle the actual scoring, considering the game's state
            return {Stone.BLACK: calculated_black_score, Stone.WHITE: calculated_white_score}
            return {Stone.BLACK: 0, Stone.WHITE: 0}

   