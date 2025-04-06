import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QMenu, QDesktopWidget
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QMovie, QPixmap, QFontDatabase, QFont
import pyautogui

class CatBreakReminder(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the custom font (dogicapixel.ttf)
        font_path = Path("dogica/TTF/dogicapixelbold.ttf").resolve()
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, 6)  # Set font size 

        # Set window properties: frameless, always on top, translucent background
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Get screen size (using pyautogui for consistency)
        screen_width, screen_height = pyautogui.size()
        window_width, window_height = 404, 445
        self.setGeometry(0, screen_height - window_height, window_width, window_height)

        # --- Load Images and Animations ---
        # Background image
        self.background_pixmap = QPixmap('sprites/cat_house.png')

        # Cat animations using QMovie
        self.movie_idle = QMovie('sprites/idle1_144.gif')
        self.move_excited = QMovie('sprites/excited_144.gif')
        self.movie_drink = QMovie('sprites/water_144.gif')
        self.move_dance = QMovie('sprites/dance_144.gif')
        self.movie_cry = QMovie('sprites/cry_144.gif')
        # Dead cat will be a static image
        self.dead_pixmap = QPixmap('sprites/DeadCat.png')

        # --- Create UI Elements ---
        # Background label
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, window_width, window_height)
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)

        # Cat label: displays the animated cat
        self.cat_label = QLabel(self)
        self.cat_label.setStyleSheet("background-color: transparent;")
        self.cat_label.setMovie(self.movie_idle)
        self.cat_label.start()  # Start with the idle animation

        # --- Define relative positioning of the cat (percentage-based) ---
        # Relative position of the cat to the background image
        self.cat_x_percent = 0.33  # 33% from the left of the background
        self.cat_y_percent = 0.12  # 12% from the top of the background

        self.update_cat_position()  # Update position on initialization

        # Status label (at the bottom)
        self.status_label = QLabel(self)
        self.status_label.setGeometry(0, window_height - 40, window_width, 20)
        self.status_label.setStyleSheet("background-color: white; color: black;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setText("Cat is watching you work...")
        self.status_label.setFont(font)  # Apply custom font
        self.status_label.setStyleSheet("color: #3b3227; background-color: #f0e5d2;")

        # Timer label (above status)
        self.timer_label = QLabel(self)
        self.timer_label.setGeometry(0, window_height - 60, window_width, 20)
        self.timer_label.setStyleSheet("background-color: white; color: black;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setText("Water: --m | Eyes: --m | Stretch: --m")
        self.timer_label.setFont(font)  # Apply custom font
        self.timer_label.setStyleSheet("color: #3b3227; background-color: #f0e5d2;")

        self.show()

    def resizeEvent(self, event):
        """
        Update the position of the cat when the window is resized.
        """
        super().resizeEvent(event)
        self.update_cat_position()

    def update_cat_position(self):
        """
        Updates the position of the cat based on the relative percentages and the window size.
        """
        # Get current window size
        window_width = self.width()
        window_height = self.height()

        # Get background size (cat_house image size)
        background_width = self.background_pixmap.width()
        background_height = self.background_pixmap.height()

        # Calculate the cat's new position
        cat_x = int(background_width * self.cat_x_percent)
        cat_y = int(background_height * self.cat_y_percent)

        # Position the cat based on background scaling
        scale_factor_x = window_width / background_width
        scale_factor_y = window_height / background_height

        # Scale cat's width/height relative to the background size
        cat_size_factor = min(scale_factor_x, scale_factor_y)
        cat_width = int(144 * cat_size_factor)  # Scale the cat's size relative to window size
        cat_height = cat_width  # Maintain the square aspect ratio

        # Update cat label size and position
        self.cat_label.setGeometry(cat_x * scale_factor_x, cat_y * scale_factor_y, cat_width, cat_height)

    # --- Initialize Reminder Timers ---
        self.start_time = time.time()
        self.water_interval = 40 * 60      # 40 minutes
        self.eye_interval = 0.1 * 60        # 20 minutes
        self.stretch_interval = 2 * 60 * 60 # 2 hours

        self.last_water_time = self.start_time
        self.last_eye_time = self.start_time
        self.last_stretch_time = self.start_time

        # Flag to indicate cat death (stop timers/animations)
        self.cat_dead = False

        # Timer to check reminders every second
        self.check_timer = QTimer(self)
        self.check_timer.setInterval(1000)
        self.check_timer.timeout.connect(self.check_timers)
        self.check_timer.start()

        # Allow dragging of the window
        self.offset = QPoint()

    def check_timers(self):
        if self.cat_dead:
            return  # Stop further processing if cat is dead

        current_time = time.time()

        # Calculate remaining times (in minutes)
        water_remaining = int((self.water_interval - (current_time - self.last_water_time)) / 60)
        eye_remaining = int((self.eye_interval - (current_time - self.last_eye_time)) / 60)
        stretch_remaining = int((self.stretch_interval - (current_time - self.last_stretch_time)) / 60)
        self.timer_label.setText(f"Water: {water_remaining}m | Eyes: {eye_remaining}m | Stretch: {stretch_remaining}m")

        # Water reminder
        if current_time - self.last_water_time >= self.water_interval:
            QSound.play("meow.wav")
            self.change_animation(self.movie_drink, "Cat is drinking water!")
            result = self.show_notification("Time to drink some water!", "water")
            if result == QMessageBox.Yes:
                self.last_water_time = current_time

        # Eye break reminder
        if current_time - self.last_eye_time >= self.eye_interval:
            QSound.play("meow.wav")
            self.change_animation(self.move_excited, "Cat is massaging their eyes!")
            result = self.show_notification("Time to take an eye break! Look at something far away for a little bit.", "eye")
            if result == QMessageBox.Yes:
                self.last_eye_time = current_time

        # Stretch reminder
        if current_time - self.last_stretch_time >= self.stretch_interval:
            QSound.play("meow.wav")
            self.change_animation(self.move_dance, "Cat is stretching with you!")
            result = self.show_notification("Time to take a stretch break!", "stretch")
            if result == QMessageBox.Yes:
                self.last_stretch_time = current_time

    def show_notification(self, message, animation_type):
        def create_dialog(msg_text):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Cat Reminder")
            msg_box.setText(msg_text)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            # Apply font and style
            msg_box.setFont(self.status_label.font())
            msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #fbd2b3;
                    }
                    QLabel {
                        color: #000000;
                        font-size: 12px;
                    }
                    QPushButton {
                        background-color: #d78c77;
                        color: #000000;
                        padding: 6px 14px;
                        border: none;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #eb9486;
                        font-size: 8px;
                    }
                    QPushButton:pressed {
                        background-color: #5E81AC;
                        font-size: 8px;
                    }
                """)

            # Force the layout to calculate before moving
            msg_box.ensurePolished()
            msg_box.adjustSize()
            msg_box.repaint()  # Force geometry update

            # Center on screen
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            msg_box_geometry = msg_box.frameGeometry()
            msg_box_geometry.moveCenter(screen_geometry.center())
            msg_box.move(msg_box_geometry.topLeft())

            return msg_box.exec_()

        # First popup
        reply = create_dialog(message + "\n\nDid you complete this task?")
        if reply == QMessageBox.Yes:
            self.change_animation(self.movie_idle, "Cat is watching you work...")
            return reply
        else:
            self.change_animation(self.movie_cry, "Cat is crying because you didn't complete the task!")
            second_reply = create_dialog("Are you sure you didn't complete the task?")
            if second_reply == QMessageBox.Yes:
                self.cat_die()
            else:
                QTimer.singleShot(50000, self.reset_to_idle)
            return reply

    def change_animation(self, movie, status_message):
        # Stop current movie and change to the new one
        self.current_movie.stop()
        self.current_movie = movie
        self.cat_label.setMovie(self.current_movie)
        self.current_movie.start()
        self.status_label.setText(status_message)

    def reset_to_idle(self):
        if not self.cat_dead:
            self.change_animation(self.movie_idle, "Cat is watching you work...")

    def cat_die(self):
        self.cat_dead = True
        self.status_label.setText("The cat has died. RIP.")
        self.cat_label.setPixmap(self.dead_pixmap)
        # Optionally stop the timer from checking further reminders
        self.check_timer.stop()

    # --- Enable Window Dragging ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    # --- Context Menu with additional options ---
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quit_action:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CatBreakReminder()
    sys.exit(app.exec_())
