from copy import deepcopy
from env.board import Board
from .mcts_git import mcts


class GameState():
    def __init__(self, board: Board):
        self.board = board

    def getPossibleActions(self):
        possible_actions = []
        for k in self.board.avail_steps[self.board.color].keys():
            for v in self.board.avail_steps[self.board.color][k]:
                possible_actions.append((k, v))
        return possible_actions

    def takeAction(self, action):
        source, target = action
        board = deepcopy(self.board)
        board.exec(source, target)
        return GameState(board)

    def isTerminal(self):
        return self.board.is_terminal


    def getReward(self):
        return (
            self.board.counts[self.board.color] > self.board.counts[-self.board.color]
        )


class MCTSEngine():
    def __init__(self):
        pass

    def exec(self, board: Board) -> (tuple, tuple):
        game_state =  GameState(deepcopy(board))
        m = mcts(iterationLimit=50)
        return m.search(initialState=game_state)


engine = MCTSEngine
