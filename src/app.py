"""
Mini Alpha-Go 主 GUI 程序
"""
import argparse
import os
import sys
from copy import deepcopy
import time
from os.path import join

from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QColor, QFont, QIcon, QMouseEvent, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from env.board import B, Board, W

GRID_SIZE = 40
OFFSET = 10
BD_SIZE = 340  # chess board size
SIDER_L = 400  # margin-left of sider
NAMES = ["", "BLACK", "WHITE"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # 脚本目录路径

parser = argparse.ArgumentParser(description="Mini Alpha-Go.")
parser.add_argument(
    "-a",
    "--engine_a",
    type=str,
    default="human",
    help="Engine for player a (black). Default: human.",
)
parser.add_argument(
    "-b",
    "--engine_b",
    type=str,
    default="human",
    help="Engine for player b (white). Default: human.",
)


class Worker(QThread):
    signal = pyqtSignal(tuple)

    def __init__(self, engine, board):
        QThread.__init__(self)
        self.engine = engine
        self.board = board

    def run(self):
        result = self.engine.exec(self.board)
        self.signal.emit(result)


class Piece(QLabel):
    """ Piece: clickable QLabel """

    clicked = pyqtSignal()

    def __init(self, parent):
        QLabel.__init__(self, QMouseEvent)

    def mousePressEvent(self, ev):
        self.clicked.emit()


class App(QMainWindow):
    round_switched = pyqtSignal()
    worker_signal = pyqtSignal()

    def __init__(self, engine_a: str, engine_b: str):
        super().__init__()
        self.title = "Mini Alpha-Go"
        self.width = 640
        self.height = 360

        self.board = Board()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.time = [None, 0, 0]

        Engine_A = __import__("engines." + engine_a).__dict__[engine_a].engine
        Engine_B = __import__("engines." + engine_b).__dict__[engine_b].engine
        self.engine = ["", Engine_A(), Engine_B()]
        self.worker_signal.connect(self.spawn_new_thread)
        self.round_switched.connect(self.run_game)

        self.black = QPixmap(join(SCRIPT_DIR, "../assets/black.png"))
        self.white = QPixmap(join(SCRIPT_DIR, "../assets/white.png"))
        self.black_h = QPixmap(join(SCRIPT_DIR, "../assets/black_half.png"))
        self.white_h = QPixmap(join(SCRIPT_DIR, "../assets/white_half.png"))
        self.chessbd = QPixmap(join(SCRIPT_DIR, "../assets/chessbd.png")).scaled(
            BD_SIZE, BD_SIZE
        )
        self.empty = QPixmap()
        self.icon_path = join(SCRIPT_DIR, "../assets/black.png")

        self.initUI()

    def initUI(self):
        # Set window title and size
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)
        self.setWindowIcon(QIcon(self.icon_path))
        self.center()

        # Set window background color to green
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor("#6F8F5F"))
        self.setPalette(p)

        # banner
        banner = QLabel("Min! A1pha-G0", self)
        banner.setFont(QFont("Arial", 20, QFont.Bold, True))
        banner.resize(200, 40)
        banner.move(SIDER_L, 20)

        # readme
        readme = QLabel("Keyboard shortcuts:\n > Esc/q: quit", self)
        readme.setFont(QFont("Consolas", 12))
        readme.resize(200, 50)
        readme.move(SIDER_L, 70)

        # Score board
        self.cur_player = QLabel("Player:", self)
        self.cur_player.setFont(QFont("Arial", 14))
        self.cur_player.resize(150, 40)
        self.cur_player.move(400, 150)

        self.name = QLabel("%s" % NAMES[self.board.color], self)
        self.name.setFont(QFont("Arial", 14, QFont.Bold))
        self.name.resize(100, 40)
        self.name.move(480, 150)
        self.name.setStyleSheet(r"QLabel {color: " + NAMES[self.board.color] + "}")

        self.b_score = QLabel("BLACK: 12", self)
        self.b_score.setFont(QFont("Consolas", 14, QFont.Bold))
        self.b_score.resize(110, 40)
        self.b_score.move(SIDER_L, 230)
        self.b_score.setStyleSheet(r"QLabel {color: black}")

        self.w_score = QLabel("WHITE: 12", self)
        self.w_score.setFont(QFont("Consolas", 14, QFont.Bold))
        self.w_score.resize(110, 40)
        self.w_score.move(SIDER_L, 250)
        self.w_score.setStyleSheet(r"QLabel {color: white}")

        # Time board
        self.b_time = QLabel("BLACK time: 0.0 s", self)
        self.b_time.setFont(QFont("Consolas", 12, QFont.Bold))
        self.b_time.resize(200, 40)
        self.b_time.move(SIDER_L, 280)
        self.b_time.setStyleSheet(r"QLabel {color: black}")

        self.w_time = QLabel("WHITE time: 0.0 s", self)
        self.w_time.setFont(QFont("Consolas", 12, QFont.Bold))
        self.w_time.resize(200, 40)
        self.w_time.move(SIDER_L, 300)
        self.w_time.setStyleSheet(r"QLabel {color: white}")

        # time duration
        self.timer.start(10)

        # Chess board
        chessbd = QLabel(self)
        chessbd.setPixmap(self.chessbd)
        chessbd.resize(BD_SIZE, BD_SIZE)

        # Pieces
        self.draw_pieces()

        # Status bar
        self.statusBar().showMessage("Ready.")

        # show ui
        self.show()

        # play
        if self.engine[B] == "human":
            pass
        elif self.engine[W] == "human":
            self.run_game()
        else:
            self.spawn_new_thread()

    def spawn_new_thread(self):
        self.t = Worker(self.engine[self.board.color], deepcopy(self.board))
        self.t.signal.connect(self.update_fromw_workers)
        self.t.start()

    def update_fromw_workers(self, result):
        if not self.board.is_terminal:
            source, target = result
            self.update_statusbar(source, target)

            self.board.exec(source, target)

            self.update_pieces()
            self.update_scoreboard()
            self.spawn_new_thread()
        else:
            winner = ["BLACK", "WHITE"][self.board.counts[W] > self.board.counts[B]]
            reply = QMessageBox.question(
                self,
                "Game over!",
                "The winner is %s! Restart the game?" % winner,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                self.board = Board()
                self.time = [None, 0, 0]
                self.update_pieces()
                self.update_scoreboard()
                self.update_time()
                self.spawn_new_thread()
            else:
                self.close()

    def run_game(self):
        if not self.board.is_terminal:
            if self.engine[self.board.color] != "human":
                source, target = self.engine[self.board.color].exec(
                    deepcopy(self.board)
                )
                self.update_statusbar(source, target)

                self.board.exec(source, target)

                self.update_pieces()
                self.update_scoreboard()
        else:
            winner = ["BLACK", "WHITE"][self.board.counts[W] > self.board.counts[B]]
            reply = QMessageBox.question(
                self,
                "Game over!",
                "The winner is %s! Restart the game?" % winner,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                self.board = Board()
                self.time = [None, 0, 0]
                self.update_pieces()
                self.update_scoreboard()
                self.update_time()
                self.run_game()
            else:
                self.close()

    def update_statusbar(self, source, target):
        if source is None:
            self.statusBar().showMessage(
                "%s cannot go, switched to %s again!"
                % (NAMES[-self.board.color], NAMES[self.board.color])
            )
        else:
            if self.board.matrix[target[0]][target[1]] != 0:
                self.statusBar().showMessage(
                    "%s ate 1 %s!" % (NAMES[self.board.color], NAMES[-self.board.color])
                )
            else:
                self.statusBar().showMessage("%s moved." % NAMES[self.board.color])

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_time(self):
        if not self.board.is_terminal:
            print(self.time[self.board.color])
            self.time[self.board.color] += 0.01
            self.b_time.setText("BLACK time: %4.1f s" % self.time[B])
            self.w_time.setText("WHITE time: %4.1f s" % self.time[W])

    def update_scoreboard(self):
        self.name.setText(NAMES[self.board.color])
        self.name.setStyleSheet(r"QLabel {color: " + NAMES[self.board.color] + "}")
        self.b_score.setText("BLACK: %d" % self.board.counts[B])
        self.w_score.setText("WHITE: %d" % self.board.counts[W])

    def draw_pieces(self):
        self.pieces = []
        self.selected_index = None
        self.avail_steps_cache = []
        for i in range(8):
            row = []
            for j in range(8):
                label = Piece(self)
                label.resize(GRID_SIZE, GRID_SIZE)
                label.move(OFFSET + GRID_SIZE * j, OFFSET + GRID_SIZE * i)
                label.index = (i, j)
                label.is_candidate = False
                label.clicked.connect(self.mouseClickEvent)
                row.append(label)
                if self.board.matrix[i][j] == B:
                    label.setPixmap(self.black)
                elif self.board.matrix[i][j] == W:
                    label.setPixmap(self.white)
                else:
                    continue
            self.pieces.append(row)

    def update_pieces(self):
        for i in range(8):
            for j in range(8):
                self.pieces[i][j].setPixmap(
                    [self.empty, self.black, self.white][self.board.matrix[i][j]]
                )
                self.pieces[i][j].is_candidate = False
                self.pieces[i][j].setStyleSheet(r"QLabel {}")

    def keyPressEvent(self, e):
        if e.key() in [Qt.Key_Escape, ord("Q")]:
            self.close()
        else:
            print(e.key())

    def mouseClickEvent(self):
        if self.engine[self.board.color] != "human":
            return

        moved = False
        sender = self.sender()
        i, j = sender.index

        # clear previous background color and recover its image
        if self.selected_index is not None:
            prev_i, prev_j = self.selected_index
            self.pieces[prev_i][prev_j].setStyleSheet(r"QLabel {}")
            if self.board.matrix[prev_i][prev_j] == B:
                self.pieces[prev_i][prev_j].setPixmap(self.black)
            elif self.board.matrix[prev_i][prev_j] == W:
                self.pieces[prev_i][prev_j].setPixmap(self.white)
            else:
                self.pieces[prev_i][prev_j].setPixmap(self.empty)

        # exec a step
        if self.pieces[i][j].is_candidate:
            moved = True
            old_color = self.board.color

            # status bar: eating happens
            if self.board.matrix[i][j] != 0:
                self.statusBar().showMessage(
                    "%s ate 1 %s!" % (NAMES[old_color], NAMES[-old_color])
                )
            else:
                self.statusBar().showMessage("%s moved." % NAMES[old_color])

            self.board.exec(self.selected_index, sender.index)

            # alert to user that color doesn't change
            if self.board.color == old_color:
                self.statusBar().showMessage(
                    "%s cannot go, switched to %s again!"
                    % (NAMES[-self.board.color], NAMES[self.board.color])
                )

            self.avail_steps_cache.remove((i, j))
            self.pieces[i][j].is_candidate = False
            self.pieces[i][j].setStyleSheet(r"QLabel {}")
            if old_color == B:
                self.pieces[i][j].setPixmap(self.black)
            else:
                self.pieces[i][j].setPixmap(self.white)

            prev_i, prev_j = self.selected_index
            self.pieces[prev_i][prev_j].setPixmap(self.empty)

            # update scoreboard
            self.update_scoreboard()

        # clear previous available steps
        for step in self.avail_steps_cache:
            cache_i, cache_j = step
            if self.board.matrix[cache_i][cache_j] == 0:
                self.pieces[cache_i][cache_j].setPixmap(self.empty)
            self.pieces[cache_i][cache_j].setStyleSheet(r"QLabel {}")
            self.pieces[cache_i][cache_j].is_candidate = False

        # highlight a piece
        if self.board.matrix[i][j] == self.board.color:
            # set new background color
            self.selected_index = sender.index
            self.pieces[i][j].setStyleSheet(r"QLabel {background-color: red}")

            # set new image
            if self.board.color == B:
                self.pieces[i][j].setPixmap(self.black_h)
            else:
                self.pieces[i][j].setPixmap(self.white_h)

            # show available steps
            avail_steps = self.board.get_avail_steps_in((i, j), self.board.color)
            for step in avail_steps:
                avail_i, avail_j = step
                # can eat an enemy
                if self.board.matrix[avail_i][avail_j] != 0:
                    self.pieces[avail_i][avail_j].setStyleSheet(
                        r"QLabel {background-color: blue}"
                    )
                elif self.board.color == B:
                    self.pieces[avail_i][avail_j].setPixmap(self.black_h)
                else:
                    self.pieces[avail_i][avail_j].setPixmap(self.white_h)
                self.pieces[avail_i][avail_j].is_candidate = True
            self.avail_steps_cache = avail_steps[:]

        # judge if this causes a terminal state
        if moved:
            self.round_switched.emit()


if __name__ == "__main__":
    args = parser.parse_args()
    app = QApplication(sys.argv)
    ex = App(args.engine_a, args.engine_b)
    sys.exit(app.exec_())
