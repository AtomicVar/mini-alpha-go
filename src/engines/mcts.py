import sys
import random
import math
import datetime

sys.path.append("..")
from env.board import Board
from copy import deepcopy


class MonteCarlo(object):
    def __init__(self, **kwargs):
        maxTime = kwargs.get('time',55)   
        maxMoves = kwargs.get('move',1000) #快速完成中的最大步数
        self.play_time = datetime.timedelta(seconds = maxTime)
        self.chess_board = Board()
        self.cumulated_states = []
        self.cumulated_states.append(self.chess_board)
        self.max_moves = maxMoves
        
        self.wins = {}  # 节点的获胜次数  索引为(player,state_matrix) 不采用(player,state)
        self.plays = {}  # 节点的访问次数
        self.C = kwargs.get("C", 1.414)  # UCT的参数C
        self.max_depth = 0

    def update(self, state):
        self.cumulated_states.append(state)

    def get_play(self, board: Board):
        self.max_depth = 0
        
        state = board
        player = state.color  # current_player(state)
        legal = list(state.avail_steps[player].keys())

        # Bail out early if there is no real choice to be made.
        if not legal:
            return None,None,None

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.play_time:
            self.run_simulation(board)
            games += 1

        #moves_states = [(p, self.board.next_state(state, p)) for p in legal]
        # 不能这么来做，因为这里产生的state和之前simulation里产生的不在同一个地址的，无法索引
        moves_states = []
        for p in legal:
            state_copy = deepcopy(state)
            for avail_target in state_copy.avail_steps[player][p]:
                state_copy.exec(p, avail_target)
                state_matrix = state_copy.hash_state()
                moves_states.append((p, avail_target, state_copy, state_matrix))
                state_copy = deepcopy(state)

        # Display the number of calls of 'run_simulation' and the
        # time elapsed.
        print(games, datetime.datetime.utcnow() - begin)
        if player == 1:
            print("Now player:", "Black")
        else:
            print("Now player:", "White")

        # Pick the move with the highest percentage of wins.

        percent_wins, move, target, next_state, state_mat = max(
            (
                (
                    self.wins.get((player, S_mat), 0)
                    / self.plays.get((player, S_mat), 1),
                    p,
                    t,
                    S,
                    S_mat,
                )
                for p, t, S, S_mat in moves_states
            ),
            key=lambda x: x[0],
        )

        # Display the stats for each possible play.

        for x in sorted(
            (
                (
                    100
                    * self.wins.get((player, S_mat), 0)
                    / self.plays.get((player, S_mat), 1),
                    self.wins.get((player, S_mat), 0),
                    self.plays.get((player, S_mat), 0),
                    p,
                )
                for p, t, S, S_mat in moves_states
            ),
            reverse=True,
        ):

            print("{3}: {0:.2f} % ({1} / {2})".format(*x))

        print("Maximum depth searched:", self.max_depth)

        
        return move,target,next_state
    
    def run_simulation(self,board):  
        plays, wins = self.plays, self.wins
        visited_states = set()
        states_copy = [board]#self.cumulated_states[:]
        

        expand = True
        flag = True
        for t in range(self.max_moves):
            state = deepcopy(states_copy[-1])
            player = state.color
            
        
            legal = list(state.avail_steps[player].keys())
            moves_states = []
            for p in legal:
                state_copy = deepcopy(state)
                for avail_target in state_copy.avail_steps[player][p]:

                    state_copy.exec(p, avail_target)
                    state_matrix = state_copy.hash_state()
                    moves_states.append((p, state_copy, state_matrix))
                    state_copy = deepcopy(state)
            
            #state_matrix 表示在当前状态下的矩阵,用字符串表示 例如：'1-11-1',用它来做索引
            """
            if all(plays.get((player, S_mat)) for p, S, S_mat in moves_states):
                # UCT算法 upper confrence bound apply into tree
                log_total = math.log(
                    sum(plays[(player, S_mat)] for p, S, S_mat in moves_states))
                value, move, state, state_mat = max([((wins[(player, S_mat)] / plays[(player, S_mat)]) +
                self.C * math.sqrt(log_total / plays[(player, S_mat)]), p, S, S_mat)
                for p, S,S_mat in moves_states]
                ,Key =lambda x : x[0])
            else:
                # Otherwise, just make an arbitrary decision.
                move, state, state_mat = random.choice(moves_states)
            """
            #flag = True
            if flag == True:
                for p,S,S_mat in moves_states:
                    if not (plays.get((player,S_mat))):
                        move = p
                        state = S
                        state_mat = S_mat
                        flag = False
                        break
            else:
                move, state, state_mat = random.choice(moves_states)
            if flag == True:
                # UCT算法 upper confrence bound apply into tree
                log_total = math.log(
                    sum(plays[(player, S_mat)] for p, S, S_mat in moves_states)
                )
                value, move, state, state_mat = max(
                    [
                        (
                            (wins[(player, S_mat)] / plays[(player, S_mat)])
                            + self.C * math.sqrt(log_total / plays[(player, S_mat)]),
                            p,
                            S,
                            S_mat,
                        )
                        for p, S, S_mat in moves_states
                    ],
                    key=lambda x: x[0],
                )
            states_copy.append(state)

            # 'player' here and below refers to the player
            # who moved into that particular state
            if expand and (player, state_mat) not in self.plays:
                expand = False
                self.plays[(player, state_mat)] = 0
                self.wins[(player, state_mat)] = 0
                if t > self.max_depth:
                    self.max_depth = t


            visited_states.add((player, state_mat))

            player = state.color
        
            if state.is_terminal:
                winner = -player
                # print(winner)
                break

        for player, state_mat in visited_states:
            if (player, state_mat) not in self.plays:
                continue
            
            self.plays[(player, state_mat)] += 1
            if player == winner:
                
                self.wins[(player, state_mat)] += 1
    def exec(self,board:Board) -> (tuple,tuple):
        
        move,t,_ = self.get_play(board)
        source = move
        target = t
        return source,target

engine = MonteCarlo
"""
if __name__ == "__main__":
    mc = MonteCarlo()
    while True:
        move,t,next_state = mc.get_play()
        if move == None:
            loser = mc.cumulated_states[-1].color
            print('The winner is ',-loser)
        #print(mc.wins)
        #print(mc.plays)
        mc.update(next_state)
"""

