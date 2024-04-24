import random
import yaml
from src.board import Board
from src.game import GameUI
from src.game import RandomAgent  # Import the RandomAgent class from game.py
from src.utils import Stone


def select_players():
    players = ['Human 1', 'AI 1', 'AI 2', 'AI 3', 'Human 2']
    print("Available players:")
    for index, player in enumerate(players, 1):
        print(f"{index}. {player}")
    selected = []
    while len(selected) < 2:
        choice = int(input(f"Select player {len(selected)+1}: ")) - 1
        if 0 <= choice < len(players) and players[choice] not in selected:
            selected.append(players[choice])
        else:
            print("Invalid selection or player already selected. Please choose again.")
    return selected

def main(config):
    selected_players = select_players()
    print(f"Starting a game with {selected_players[0]} and {selected_players[1]}")
    game_ui = GameUI(config)
    
    # Set initial turn based on player selection
    if selected_players[0] == 'Human 1':
         game_ui.turn = Stone.BLACK
    elif 'Human 2' in selected_players:
         game_ui.turn = Stone.BLACK
    elif 'AI 1' in selected_players:
         game_ui.turn = Stone.BLACK
         game_ui.ai = RandomAgent(Stone.WHITE)
    elif 'AI 2' in selected_players:
         game_ui.turn = Stone.WHITE
         game_ui.ai = RandomAgent(Stone.BLACK)
    elif 'AI 3' in selected_players:
         game_ui.turn = Stone.BLACK  # or Stone.WHITE, depending on your preference
         game_ui.ai = RandomAgent(Stone.WHITE)
    
        # Check if AI agent is set
    if game_ui.ai is not None:
        # Start the game loop
        game_ui.play()
    else:
        print("Error: AI agent not initialized correctly.") 
        
    # Check if AI 2 is selected
    if 'AI 2' in selected_players:
        # Make a random move for AI 2
        ai_2_color = game_ui.turn
        random_agent = RandomAgent(ai_2_color)
        ai_2 = RandomAgent('WHITE')

       # move = random_agent.get_action(game_ui.game.board)
        # Get legal moves
        legal_actions = game_ui.game.board.get_legal_actions(ai_2_color)
        
        if legal_actions:
            move = random_agent.get_action(game_ui.game.board)
        
            # Convert move to (y, x) format
            if move:
                row, col = move
                game_ui._place_stone((row, col))
            
            else:
                print("No legal moves available for AI 2.")
                
        # In your main loop or function where the game is played
        if ai_2_color == 'BLACK':
            ai_2 = RandomAgent(Stone.BLACK)
        else:
            ai_2 = RandomAgent(Stone.WHITE)

    # Inside the loop where you get the AI action
    if selected_players == ai_2_color:
        move = ai_2.get_action(game_ui.game.board)
        print(f"AI 2 move: {move}")  # Debug print
        if move:
            game_ui.game._place_stone(ai_2.color, *move)

    
    game_ui.play()
    
if __name__ == '__main__':
    
    config = None
    with open('config.yaml', 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f'Error: {e}')

    if config is not None:
        main(config)