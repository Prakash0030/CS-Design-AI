import yaml
from src.board import Board
from src.game import GameUI

def select_players():
    players = ['Human', 'AI 1', 'AI 2', 'AI 3']
    print("Available players:")
    for index, player in enumerate(players, 1):
        print(f"{index}. {player}")
    selected = []
    while len(selected) < 2:
        choice = int(input(f"Select player {len(selected)+1}: ")) - 1
        if 0 <= choice < len(players):
            selected.append(players[choice])
        else:
            print("Invalid selection or player already selected. Please choose again.")
    return selected

def main(config):
    selected_players = select_players()
    print(f"Starting a game with {selected_players[0]} and {selected_players[1]}")
    game = GameUI(config, selected_players[0], selected_players[1])
    game.play()
    
if __name__ == '__main__':
    
    config = None
    with open('config.yaml', 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f'Error: {e}')

    if config is not None:
        main(config)
