import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QPixmap
import pyautogui

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties: frameless, always on top, and transparent background
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Get screen size to place it at bottom-left
        screen = QApplication.primaryScreen().geometry()
        
        # Set the size of the window and its position
        window_width = 300  # Increase width
        window_height = 300  # Increase height
        self.setGeometry(0, screen.height() - window_height, window_width, window_height)
        
        # Create background label for cat_house.png
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, window_width, window_height)
        pixmap = QPixmap('sprites/sheets/rooms/Room1.png')
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        
        # Create label for animated GIF (cat)
        self.label = QLabel(self)
        self.label.setStyleSheet("background-color: transparent;")
        self.label.setGeometry(0, 0, window_width, window_height)
        
        # Load the animated GIF
        self.movie = QMovie('sprites/idle1_5cm.gif')
        self.label.setMovie(self.movie)
        self.movie.start()
        
        # Ensure the animated GIF label is on top of the background
        self.label.raise_()
        
        # Show the window
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransparentWindow()
    sys.exit(app.exec_())
