import random

class RandomAI:
    def nextMove(self, gameUI):
        actions = gameUI.game.board.get_legal_actions(gameUI.turn)
        return random.choice(actions) if actions else None
