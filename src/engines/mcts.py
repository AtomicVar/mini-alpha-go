import sys
import numpy as numpy
import random
import math
import datetime
from env.board import Board
from copy import deepcopy
class MonteCarlo(object):
    def __init__(self, chess_board, **kwargs):
        maxTime = kwargs.get('time',60)   
        maxMoves = kwargs.get('move',1000) #快速完成中的最大步数
        self.play_time = datetime.timedelta(seconds = maxTime)
        self.chess_board = chess_board
        self.cumulated_states = []
        self.max_moves = maxMoves
        #self.current_player = B#self.chess_board.color
        self.wins = {}  #节点的获胜次数
        self.plays = {} #节点的访问次数
        self.C = kwargs.get('C', 1.414) #UCT的参数C
        self.max_depth = 0
    def update(self,state):
        self.cumulated_state.append(state)

    def get_play(self):
        self.max_depth = 0
        state = self.cumulated_states[-1]
        player = state.current_player(state)
        legal = list(state.avail_steps[player].keys())

        # Bail out early if there is no real choice to be made.
        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation()
            games += 1

        #moves_states = [(p, self.board.next_state(state, p)) for p in legal]
        moves_states = []
        for p in legal:
            state_copy = deepcopy(state)
            for avail_target in state_copy.avail_steps[player][p]:
                state_copy.exec(p,avail_target)
                moves_states.append((p,state_copy))

        # Display the number of calls of 'run_simulation' and the 
        # time elapsed.
        print(games, datetime.datetime.utcnow() - begin)

        # Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            (self.wins.get((player, S), 0) / self.plays.get((player, S), 1),
            p) for p, S in moves_states
        )

        # Display the stats for each possible play.
        for x in sorted(
            ((100 * self.wins.get((player, S), 0) / self.plays.get((player, S), 1),
            self.wins.get((player, S), 0),
            self.plays.get((player, S), 0), p)
            for p, S in moves_states),
            reverse = True
        ):
            print("{3}: {0:.2f} % ({1} / {2})".format(*x))

        print("Maximum depth searched:", self.max_depth)

        return move
    
    def run_simulation(self):  
        plays, wins = self.plays, self.wins
        visited_states = set()
        states_copy = self.cumulated_states[:]
        #state = deepcopy(states_copy[-1])
        #player = state.get_current_player()

        expand = True
        for t in range(self.max_moves):
            state = deepcopy(states_copy[-1])
            player = state.get_current_player()
            """
            legal = state.avail_steps[player].keys()#....如果不能return avail step给我，可能得做2次那个函数

            choice_source = random.choice(list(legal))
            choice_target = random.choice(state.avail_steps[player][choice_source])
            state.exec(choice_source,choice_target)
            """
            legal = list(state.avail_steps[player].keys())
            moves_states = []
            for p in legal:
                state_copy = deepcopy(state)
                for avail_target in state_copy.avail_steps[player][p]:
                    state_copy.exec(p,avail_target)
                    moves_states.append((p,state_copy))
            
            if all(plays.get((player, S)) for p, S in moves_states):
                # UCT算法 upper confrence bound apply into tree
                log_total = math.log(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(((wins[(player, S)] / plays[(player, S)]) +
                self.C * math.sqrt(log_total / plays[(player, S)]), p, S)
                for p, S in moves_states)
            else:
                # Otherwise, just make an arbitrary decision.
                move, state = random.choice(moves_states)

            #state = self.chess_board.next_state(state, play) #这里要改过，state自动在board里变成下个状态
            states_copy.append(state)

            # 'player' here and below refers to the player
            # who moved into that particular state
            if expand and (player, state) not in self.plays:
                expand = False
                self.plays[(player, state)] = 0
                self.wins[(player, state)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, state))

            player = state.get_current_player()
            winner = state.is_terminal()
            if winner:
                break

        for player, state in visited_states:
            if (player, state) not in self.plays:
                continue
            self.plays[(player, state)] += 1
            if player == winner:
                self.wins[(player, state)] += 1