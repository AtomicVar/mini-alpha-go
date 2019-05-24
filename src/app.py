"""
Mini Alpha-Go 主 GUI 程序
"""
import sys
import os
from os.path import join
import time
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QDesktopWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLCDNumber,
)
from PyQt5.QtGui import QPainter, QPalette, QColor, QPixmap, QFont, QIcon, QMouseEvent
from PyQt5.QtCore import pyqtSignal, Qt
from board import Board, B, W

GRID_SIZE = 40
OFFSET = 10
BD_SIZE = 340
SIDER_L = 400

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # 脚本目录路径


class Piece(QLabel):
    """ Piece: clickable QLabel """

    clicked = pyqtSignal()

    def __init(self, parent):
        QLabel.__init__(self, QMouseEvent)

    def mousePressEvent(self, ev):
        self.clicked.emit()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Mini Alpha-Go"
        self.width = 640
        self.height = 360

        self.board = Board()

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
        banner = QLabel("Mini Alpha-Go", self)
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
        self.name = QLabel("%s" % ["", "BLACK", "WHITE"][self.board.color], self)
        self.name.setFont(QFont("Arial", 14, QFont.Bold))
        self.name.resize(100, 40)
        self.name.move(480, 150)
        self.name.setStyleSheet(
            r"QLabel {color: " + ["", "black", "white"][self.board.color] + "}"
        )
        self.b_score = QLabel("BLACK: 12", self)
        self.b_score.setFont(QFont("Consolas", 14, QFont.Bold))
        self.b_score.resize(100, 40)
        self.b_score.move(SIDER_L, 230)
        self.b_score.setStyleSheet(r"QLabel {color: black}")
        self.w_score = QLabel("WHITE: 12", self)
        self.w_score.setFont(QFont("Consolas", 14, QFont.Bold))
        self.w_score.resize(100, 40)
        self.w_score.move(SIDER_L, 250)
        self.w_score.setStyleSheet(r"QLabel {color: white}")

        # Chess board
        chessbd = QLabel(self)
        chessbd.setPixmap(self.chessbd)
        chessbd.resize(BD_SIZE, BD_SIZE)

        # Pieces
        self.draw_pieces()

        # Status bar
        self.statusBar().showMessage("Ready.")

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def render_scoreboard(self):
        self.name.setText(["", "BLACK", "WHITE"][self.board.color])
        self.name.setStyleSheet(
            r"QLabel {color: " + ["", "black", "white"][self.board.color] + "}"
        )
        self.b_score.setText("BLACK: %d" % self.board.scores[B])
        self.w_score.setText("WHITE: %d" % self.board.scores[W])

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
                    label.color = B
                elif self.board.matrix[i][j] == W:
                    label.setPixmap(self.white)
                    label.color = W
                else:
                    label.color = None
                    continue
            self.pieces.append(row)

    def keyPressEvent(self, e):
        if e.key() in [Qt.Key_Escape, ord("Q")]:
            self.close()
        else:
            print(e.key())

    def mouseClickEvent(self):
        sender = self.sender()
        self.statusBar().showMessage(str(sender.index) + " is clicked!!")
        i, j = sender.index

        # clear previous background color and recover its image
        if self.selected_index is not None:
            prev_i, prev_j = self.selected_index
            self.pieces[prev_i][prev_j].setStyleSheet(r"QLabel {}")
            if self.pieces[prev_i][prev_j].color == B:
                self.pieces[prev_i][prev_j].setPixmap(self.black)
            elif self.pieces[prev_i][prev_j].color == W:
                self.pieces[prev_i][prev_j].setPixmap(self.white)
            else:
                self.pieces[prev_i][prev_j].setPixmap(self.empty)

        # exec a step
        if self.pieces[i][j].is_candidate:
            old_color = self.board.color

            self.board.exec(self.board.color, (i, j))

            self.avail_steps_cache.remove((i, j))
            self.pieces[i][j].is_candidate = False
            self.pieces[i][j].color = old_color
            if old_color == B:
                self.pieces[i][j].setPixmap(self.black)
            else:
                self.pieces[i][j].setPixmap(self.white)

            prev_i, prev_j = self.selected_index
            self.pieces[prev_i][prev_j].setPixmap(self.empty)
            self.pieces[prev_i][prev_j].color = None

            # update scoreboard
            self.render_scoreboard()

        # clear previous available steps
        for step in self.avail_steps_cache:
            cache_i, cache_j = step
            self.pieces[cache_i][cache_j].setPixmap(self.empty)
            self.pieces[cache_i][cache_j].is_candidate = False

        # highlight a piece
        if self.pieces[i][j].color == self.board.color:
            color = self.pieces[i][j].color
            # set new background color
            self.selected_index = sender.index
            self.pieces[i][j].setStyleSheet(r"QLabel {background-color: red}")

            # set new image
            if color == B:
                self.pieces[i][j].setPixmap(self.black_h)
            else:
                self.pieces[i][j].setPixmap(self.white_h)

            # show available steps
            avail_steps = self.board.get_avail_steps_in((i, j), color)
            for step in avail_steps:
                avail_i, avail_j = step
                # can eat an enemy
                if self.pieces[avail_i][avail_j].color is not None:
                    self.pieces[avail_i][avail_j].setStyleSheet(
                        r"QLabel {background-color: blue}"
                    )
                elif color == B:
                    self.pieces[avail_i][avail_j].setPixmap(self.black_h)
                else:
                    self.pieces[avail_i][avail_j].setPixmap(self.white_h)
                self.pieces[avail_i][avail_j].is_candidate = True
            self.avail_steps_cache = avail_steps[:]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
