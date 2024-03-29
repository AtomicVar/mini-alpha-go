"""
棋盘类：Board

可访问接口：

    matrix (2d-array) 数字含义：
        0 - 无棋
        1 - 黑棋
       -1 - 白棋

    color (int): 当前准备下棋的颜色

    avail_steps (dict): 存储当前黑白方能走的位置
        {
            B: {
                (0, 1): [(1, 1), (2, 2)]
                (4, 3): [(0, 0)],
                (5, 5): [],
                ...
            },
            W: {
                ...
            }
        }

    counts (dict): 当前双方棋子数量
        {
            B: 12,
            W: 12
        }
    
    is_terminal (bool): 是否处于终止状态（双方都无棋可下，或一方棋子仅剩下一颗，或某一方连起来）
"""

B = 1
W = -1


class Board:
    def __init__(self):
        self.matrix = [x[:] for x in [[0] * 8] * 8]  # 2d array
        for i in range(1, 7):
            self.matrix[0][i] = 1
            self.matrix[7][i] = 1
            self.matrix[i][0] = -1
            self.matrix[i][7] = -1

        self.row_checkers = [6, 2, 2, 2, 2, 2, 2, 6]
        self.col_checkers = [6, 2, 2, 2, 2, 2, 2, 6]
        self.maindiag_checkers = [0, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2]
        self.paradiag_checkers = [0, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2]

        self.color = B
        self.avail_steps = {B: self.get_avail_steps(B), W: {}}
        self.counts = {B: 12, W: 12}
        self.is_terminal = False

    def exec(self, source: tuple, target: tuple) -> None:
        if source is None:
            return
        if self.is_connected():
            self.is_terminal = True
            self.color *= -1
            return

        t_row, t_col = target
        s_row, s_col = source

        # safety checking
        assert self.matrix[s_row][s_col] == self.color
        assert target in self.avail_steps[self.color][source]

        # clear source
        self.matrix[s_row][s_col] = 0

        # may update counts
        if self.matrix[t_row][t_col] == -self.color:
            self.counts[-self.color] -= 1

        # update checkers count
        self.row_checkers[s_row] -= 1
        self.col_checkers[s_col] -= 1
        self.maindiag_checkers[s_col - s_row] -= 1
        self.paradiag_checkers[7 - s_col - s_row] -= 1
        if self.matrix[t_row][t_col] == 0:
            self.row_checkers[t_row] += 1
            self.col_checkers[t_col] += 1
            self.maindiag_checkers[t_col - t_row] += 1
            self.paradiag_checkers[7 - t_col - t_row] += 1

        # set target
        self.matrix[t_row][t_col] = self.color

        # update available cache
        self.avail_steps[-self.color] = self.get_avail_steps(-self.color)

        # test if is terminal
        if self.counts[-self.color] == 1:
            self.is_terminal = True
        elif self.is_connected():
            self.is_terminal = True

        # if enemy cannot go, also update my available cache, and do not invert color
        if len(self.avail_steps[-self.color]) == 0:
            self.avail_steps[self.color] = self.get_avail_steps(self.color)
            # if me cannot go either, set current board to is_terminal
            if len(self.avail_steps[self.color]) == 0:
                self.is_terminal = True
        else:
            self.color *= -1

    def is_connected(self):
        cur_label = 0
        labels = [[0 for _ in range(8)] for _ in range(8)]
        equiv_labels = {}

        def get_label_left(i, j):
            if j == 0:
                return 0
            else:
                return labels[i][j - 1]

        def get_label_lefttop(i, j):
            if j == 0 or i == 0:
                return 0
            else:
                return labels[i - 1][j - 1]

        def get_label_top(i, j):
            if i == 0:
                return 0
            else:
                return labels[i - 1][j]

        def get_label_righttop(i, j):
            if i == 0 or j == 7:
                return 0
            else:
                return labels[i - 1][j + 1]

        # first pass
        for i in range(8):
            for j in range(8):
                if self.matrix[i][j] == self.color:
                    four_labels = [get_label_left(i, j),get_label_lefttop(i, j),get_label_righttop(i, j),get_label_top(i, j) ]
                    zeros = []
                    non_zeros = []
                    for k in range(4):
                        if four_labels[k] == 0:
                            zeros.append(four_labels[k])
                        elif four_labels[k] not in non_zeros:
                            non_zeros.append(four_labels[k])
                    if len(zeros) == 4:
                        labels[i][j] = cur_label + 1
                        cur_label += 1
                    elif len(non_zeros) == 1:
                        labels[i][j] = non_zeros[0]
                    else:
                        labels[i][j] = non_zeros[0]
                        if four_labels[0] in equiv_labels:
                            equiv_labels[four_labels[0]].append(four_labels[1])
                        else:
                            equiv_labels[four_labels[0]] = [four_labels[1]]
        # second pass
        max_label = 0
        for i in range(8):
            for j in range(8):
                if self.matrix[i][j] == self.color:
                    if labels[i][j] in equiv_labels:
                        labels[i][j] = min(labels[i][j], *equiv_labels[labels[i][j]])
                    max_label = max(max_label, labels[i][j])
        # from pprint import pprint
        # pprint(labels)
        # print(max_label)
        return max_label == 1
        
    def get_avail_steps(self, color: int) -> dict:
        steps = {}
        for i in range(8):
            for j in range(8):
                if self.matrix[i][j] == color:
                    n_row = self.row_checkers[i]
                    n_col = self.col_checkers[j]
                    n_md = self.maindiag_checkers[j - i]
                    n_pd = self.paradiag_checkers[7 - j - i]

                    # 向右走
                    if j + n_row < 8 and self.matrix[i][j + n_row] != color:
                        no_enemy = True
                        for col in range(j + 1, j + n_row):
                            if self.matrix[i][col] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i, j + n_row))
                            else:
                                steps[(i, j)] = [(i, j + n_row)]

                    # 向左走
                    if j - n_row >= 0 and self.matrix[i][j - n_row] != color:
                        no_enemy = True
                        for col in range(j - 1, j - n_row, -1):
                            if self.matrix[i][col] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i, j - n_row))
                            else:
                                steps[(i, j)] = [(i, j - n_row)]

                    # 向下走
                    if i + n_col < 8 and self.matrix[i + n_col][j] != color:
                        no_enemy = True
                        for row in range(i + 1, i + n_col):
                            if self.matrix[row][j] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i + n_col, j))
                            else:
                                steps[(i, j)] = [(i + n_col, j)]

                    # 向上走
                    if i - n_col >= 0 and self.matrix[i - n_col][j] != color:
                        no_enemy = True
                        for row in range(i - 1, i - n_col, -1):
                            if self.matrix[row][j] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i - n_col, j))
                            else:
                                steps[(i, j)] = [(i - n_col, j)]

                    # 向右上走
                    if (
                        i - n_pd >= 0
                        and j + n_pd < 8
                        and self.matrix[i - n_pd][j + n_pd] != color
                    ):
                        no_enemy = True
                        for d in range(1, n_pd):
                            if self.matrix[i - d][j + d] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i - n_pd, j + n_pd))
                            else:
                                steps[(i, j)] = [(i - n_pd, j + n_pd)]

                    # 向左下走
                    if (
                        i + n_pd < 8
                        and j - n_pd >= 0
                        and self.matrix[i + n_pd][j - n_pd] != color
                    ):
                        no_enemy = True
                        for d in range(1, n_pd):
                            if self.matrix[i + d][j - d] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i + n_pd, j - n_pd))
                            else:
                                steps[(i, j)] = [(i + n_pd, j - n_pd)]

                    # 向左上走
                    if (
                        i - n_md >= 0
                        and j - n_md >= 0
                        and self.matrix[i - n_md][j - n_md] != color
                    ):
                        no_enemy = True
                        for d in range(1, n_md):
                            if self.matrix[i - d][j - d] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i - n_md, j - n_md))
                            else:
                                steps[(i, j)] = [(i - n_md, j - n_md)]

                    # 向右下走
                    if (
                        i + n_md < 8
                        and j + n_md < 8
                        and self.matrix[i + n_md][j + n_md] != color
                    ):
                        no_enemy = True
                        for d in range(1, n_md):
                            if self.matrix[i + d][j + d] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i + n_md, j + n_md))
                            else:
                                steps[(i, j)] = [(i + n_md, j + n_md)]
        return steps

    def get_avail_steps_in(self, loc: tuple, color) -> list:
        if loc in self.avail_steps[color]:
            return self.avail_steps[color][loc]
        else:
            return []

    def can_color_go(self, color: int) -> bool:
        return len(self.avail_steps[color]) > 0

    def print_board(self) -> None:
        from pprint import pprint

        pprint(self.matrix)

    def hash_state(self) -> str:
        ret = ""
        for row in range(8):
            for col in range(8):
                ret += str(self.matrix[row][col])
        return ret


if __name__ == "__main__":
    board = Board()
    board.print_board()
    print(board.is_connected())
