"""
棋盘类：Board

矩阵数字含义：
  0 - 无棋
  1 - 黑棋
 -1 - 白棋
"""

B = 1
W = -1


class Board():
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
        self.scores = {B: 8, W: 8}

    def exec(self, color: int, loc: tuple) -> None:
        row, col = loc
        self.matrix[row][col] = color
        self.avail_steps[-color] = self.get_avail_steps(-color)
        self.color = -self.color

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
                    if i - n_md >= 0 and j + n_md < 8 and self.matrix[
                            i - n_md][j + n_md] != color:
                        no_enemy = True
                        for d in range(1, n_md):
                            if self.matrix[i - d][j + d] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i - n_md, j + n_md))
                            else:
                                steps[(i, j)] = [(i - n_md, j + n_md)]

                    # 向左下走
                    if i + n_md < 8 and j - n_md >= 0 and self.matrix[
                            i + n_md][j - n_md] != color:
                        no_enemy = True
                        for d in range(1, n_md):
                            if self.matrix[i + d][j - d] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i + n_md, j - n_md))
                            else:
                                steps[(i, j)] = [(i + n_md, j - n_md)]

                    # 向左上走
                    if i - n_pd >= 0 and j - n_pd >= 0 and self.matrix[
                            i - n_pd][j - n_pd] != color:
                        no_enemy = True
                        for d in range(1, n_pd):
                            if self.matrix[i - d][j - d] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i - n_pd, j - n_pd))
                            else:
                                steps[(i, j)] = [(i - n_pd, j - n_pd)]

                    # 向右下走
                    if i + n_pd < 8 and j + n_pd < 8 and self.matrix[i + n_pd][
                            j + n_pd] != color:
                        no_enemy = True
                        for d in range(1, n_pd):
                            if self.matrix[i + d][j + d] == -color:
                                no_enemy = False
                                break
                        if no_enemy:
                            if (i, j) in steps:
                                steps[(i, j)].append((i + n_pd, j + n_pd))
                            else:
                                steps[(i, j)] = [(i + n_pd, j + n_pd)]
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


if __name__ == "__main__":
    board = Board()
    board.print_board()
