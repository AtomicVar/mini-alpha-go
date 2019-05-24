import random
from env.board import Board


class RandomEngine:
    def __init__(self):
        pass

    def exec(self, board: Board) -> (tuple, tuple):
        if len(board.avail_steps[board.color]) == 0:
            return None, None
        else:
            source = random.choice(list(board.avail_steps[board.color].keys()))
            target = random.choice(board.avail_steps[board.color][source])
            return source, target


engine = RandomEngine
