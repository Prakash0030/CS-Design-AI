import random

class RandomAI:
    def nextMove(self, gameUI):
        actions = gameUI.game.board.get_legal_actions(gameUI.turn)
        if len(actions) < 1:
            {
               print("testing")
            }
        return random.choice(actions) if actions else None
