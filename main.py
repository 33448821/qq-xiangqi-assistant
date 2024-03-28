import sys
import threading
import time

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QSpinBox, QComboBox
from PyQt5.QtGui import QPainter, QFont, QPen
from PyQt5.QtCore import Qt, QTimer
import win32gui
from engine import run_chess_engine
from analysis import img2fen, check_turn
import pyautogui


class MyWidget(QWidget):
    def __init__(self):
        self.my_offset = None
        self.opponent_offset = None
        self.auto_chess = False
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Set window flags to stay on top
        self.setFixedSize(1024, 738)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 位置跟随游戏窗口
        self.timer_update_position = QTimer(self)
        self.timer_update_position.timeout.connect(self.update_position)
        self.timer_update_position.start(10)  # Update position every second

        self.b1 = self.createButton("思考下步", 796, 210, self.onThinkNext)
        self.b2 = self.createButton("自动下棋", 796, 250, self.onAutoChess)
        self.b3 = self.createButton("退出程序", 796, 290, self.onExit)

        # 创建标签和数字编辑框
        self.label = QLabel("设置思考用时:", self)
        self.label.setGeometry(800, 332, 70, 20)
        self.label.setStyleSheet("color: white;")
        self.spinBox = QSpinBox(self)
        self.spinBox.setGeometry(900, 332, 90, 20)
        self.spinBox.setValue(3)

        # 创建信息条
        self.msg_label = QLabel("信息:初始化完成.", self)
        self.msg_label.setGeometry(15, 705, 800, 30)
        self.msg_label.setStyleSheet("color: white;")
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(14)
        font.bold()
        self.msg_label.setFont(font)

        # 创建自动下棋定时器
        self.timer_auto_chess = QTimer()
        self.timer_auto_chess.timeout.connect(self.executeAutoChess)

        # 引擎多选列表框
        self.label = QLabel("设置思考引擎:", self)
        self.label.setGeometry(800, 355, 70, 20)
        self.label.setStyleSheet("color: white;")
        self.comboBox = QComboBox(self)
        self.comboBox.setGeometry(900, 355, 90, 20)
        self.comboBox.addItems(['皮卡鱼3.14', '旋风6.2'])

    def createButton(self, text, x, y, onClickfunction):
        btn = QPushButton(text, self)
        btn.clicked.connect(onClickfunction)
        btn.setGeometry(x, y, 212, 40)
        btn.setStyleSheet(
            "QPushButton {"
            "   border: 1px solid #c4c4c4;"
            "   background-color: #f5f7fa;"
            "   color: #606266;"
            "   font-size: 12px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #e6e9ec;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #d3d9df;"
            "}"
        )
        return btn

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.my_offset is not None and self.opponent_offset is not None:
            self.drawRectangles(qp, self.my_offset, self.opponent_offset)  # Use stored offsets
        qp.end()

    def setOffsets(self, my_offset, opponent_offset):
        self.my_offset = my_offset
        self.opponent_offset = opponent_offset
        self.update()  # Trigger repaint

    def process_thinking(self):
        engine_id = self.comboBox.currentIndex()
        start_time = time.time()
        fen = img2fen()
        print(fen)
        my_offset, opponent_offset = run_chess_engine(self.spinBox.value() * 1000, fen, engine_id)
        self.setOffsets(my_offset, opponent_offset)
        self.update()

        elapsed_time = time.time() - start_time
        elapsed_time_formatted = "{:.2f}".format(elapsed_time)
        self.logger(f'思考完成，读取棋盘 + 思考共耗时：{elapsed_time_formatted} 秒, 当前引擎：{self.comboBox.currentText()}')

    def onThinkNext(self):
        # 在一个新的线程中运行思考下一步
        thread = threading.Thread(target=self.process_thinking)
        thread.start()
        thread.join()

    def onAutoChess(self):
        if self.auto_chess:
            self.auto_chess = False
        else:
            self.auto_chess = True

        if self.auto_chess:
            self.b2.setText('停止下棋')
            self.timer_auto_chess.start(self.spinBox.value() + 1000)
        else:
            self.b2.setText('自动下棋')
            self.timer_auto_chess.stop()

    def executeAutoChess(self):
        thread = threading.Thread(target=self.thread_auto_chess)
        thread.start()
        thread.join()

    def thread_auto_chess(self):
        if check_turn():
            start_time = time.time()
            # 在这里放置原本在按钮点击时执行的代码
            self.logger("自动下棋中...")
            fen = img2fen()
            engine_id = self.comboBox.currentIndex()
            my_offset, opponent_offset = run_chess_engine(self.spinBox.value() * 1000, fen, engine_id)
            self.setOffsets(my_offset, opponent_offset)
            x, y, x_to, y_to, w, h = self.calculateCoordinates(self.my_offset)
            self.update()

            elapsed_time = time.time() - start_time
            elapsed_time_formatted = "{:.2f}".format(elapsed_time)
            self.logger(f'思考完成，读取棋盘 + 思考共耗时：{elapsed_time_formatted} 秒, 当前引擎：{self.comboBox.currentText()}')

            # 获取窗口的位置信息
            window_rect = self.geometry()
            window_x = window_rect.x()
            window_y = window_rect.y()

            # 计算相对于屏幕的绝对坐标
            click_x1 = window_x + x + 25
            click_y1 = window_y + y + 25
            click_x2 = window_x + x_to + 25
            click_y2 = window_y + y_to + 25

            pyautogui.click(x=click_x1, y=click_y1)

            pyautogui.click(x=click_x2, y=click_y2)

    def onExit(self):
        app.exit()

    def update_position(self):
        target_window_title = "QQ新中国象棋"
        target_window_handle = win32gui.FindWindow(None, target_window_title)
        if target_window_handle == 0:
            self.hide()
            return

        rect = win32gui.GetWindowRect(target_window_handle)
        x, y, width, height = rect
        self.move(x, y)
        self.resize(width, height)
        self.show()

    def calculateCoordinates(self, offset):
        from_x, from_y, to_x, to_y = offset
        rect_width = 52
        rect_height = 52
        x1 = box_left(from_x)
        y1 = box_top(from_y)
        x2 = box_left(to_x)
        y2 = box_top(to_y)
        return x1, y1, x2, y2, rect_width, rect_height

    def drawRectangles(self, qp, my_offset, opponent_offset):
        # Extract coordinates for player's rectangles
        my_x1, my_y1, my_x2, my_y2, rect_width, rect_height = self.calculateCoordinates(my_offset)
        opponent_x1, opponent_y1, opponent_x2, opponent_y2, _, _ = self.calculateCoordinates(opponent_offset)

        # Set dark green color for the pen
        pen = QPen(Qt.darkGreen, 3, Qt.SolidLine)
        qp.setPen(pen)

        # Draw player's rectangles
        qp.drawRect(my_x1, my_y1, rect_width, rect_height)
        qp.drawRect(my_x2, my_y2, rect_width, rect_height)

        # Set red color for the pen
        pen.setColor(Qt.darkBlue)
        qp.setPen(pen)

        # Draw opponent's rectangles
        qp.drawRect(opponent_x1, opponent_y1, rect_width, rect_height)
        qp.drawRect(opponent_x2, opponent_y2, rect_width, rect_height)

    def logger(self, msg):
        self.msg_label.setText('信息：' + msg)
        self.update()
        print(msg)


def box_left(letter):
    # 确定字母在字母表中的位置（a对应1，b对应2，依此类推）
    alphabet_index = ord(letter) - ord('a') + 1

    # 计算值并返回
    value = 241 + (alphabet_index - 1) * 57
    return value


def box_top(in_num):
    if in_num.isdigit():
        input_value = int(in_num)
    else:
        return "Invalid input"

    value = 590 - input_value * 57
    return value


if __name__ == '__main__':
    app = QApplication(sys.argv)

    my_widget = MyWidget()
    my_widget.setWindowTitle('QQ新中国象棋助手')
    my_widget.show()

    sys.exit(app.exec_())
