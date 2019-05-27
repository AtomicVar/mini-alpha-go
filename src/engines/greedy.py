"""
Greedy engine: try to choose one step that can eat an enemy, else, choose one randomly.
"""
import random
from env.board import Board


class GreedyEngine:
    def __init__(self):
        pass

    def exec(self, board: Board) -> (tuple, tuple):
        if len(board.avail_steps[board.color]) == 0:
            return None, None
        else:
            awail_steps = list(board.avail_steps[board.color].keys())
            for source in awail_steps:
                for target in board.avail_steps[board.color][source]:
                    if board.matrix[target[0]][target[1]] == -board.color:
                        return source, target

            source = random.choice(list(board.avail_steps[board.color].keys()))
            target = random.choice(board.avail_steps[board.color][source])
            return source, target


engine = GreedyEngine
