import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
import pyautogui

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Get screen size to place it at bottom-left
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, screen.height() - 100, 100, 100)

        # Set the size of the window and its position
        window_width = 300  # Increase width
        window_height = 300  # Increase height
        self.setGeometry(0, screen.height() - window_height, window_width, window_height)  # Set position and size
        
        # Create label for GIF
        self.label = QLabel(self)
        self.label.setStyleSheet("background-color: transparent;")
        self.label.setGeometry(0, 0, window_width, window_height)  # Resize label to match the window size
        
        # Load the animated GIF
        self.movie = QMovie('sprites/idle1_5cm.gif')
        self.label.setMovie(self.movie)
        
        # Start the animation
        self.movie.start()
        
        # Show the window
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransparentWindow()
    sys.exit(app.exec_())