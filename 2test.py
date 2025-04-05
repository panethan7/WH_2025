import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QMenu
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QMovie, QPixmap
import pyautogui

class CatBreakReminder(QMainWindow):
    def __init__(self):
        super().__init__()

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
        self.cat_label.setGeometry(137, 53, window_width, window_height)
        self.cat_label.setStyleSheet("background-color: transparent;")
        # Start with the idle animation
        self.current_movie = self.movie_idle
        self.cat_label.setMovie(self.current_movie)
        self.current_movie.start()

        # Status label (at the bottom)
        self.status_label = QLabel(self)
        self.status_label.setGeometry(0, window_height - 40, window_width, 20)
        self.status_label.setStyleSheet("background-color: white; color: black;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setText("Cat is watching you work...")

        # Timer label (above status)
        self.timer_label = QLabel(self)
        self.timer_label.setGeometry(0, window_height - 60, window_width, 20)
        self.timer_label.setStyleSheet("background-color: white; color: black;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setText("Water: --m | Eyes: --m | Stretch: --m")

        # --- Initialize Reminder Timers ---
        self.start_time = time.time()
        self.water_interval = 0.1 * 60      # 40 minutes
        self.eye_interval = 20 * 60        # 20 minutes
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

        self.show()

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
            self.change_animation(self.move_excited, "Cat is napping while you rest your eyes!")
            result = self.show_notification("Time to take an eye break! Look at something far away for 20 seconds.", "eye")
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
        # First confirmation popup
        reply = QMessageBox.question(self, "Cat Reminder",
                                     message + "\n\nDid you complete this task?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.change_animation(self.movie_idle, "Cat is watching you work...")
            return reply
        else:
            # If first answer is No, show crying animation and ask again
            self.change_animation(self.movie_cry, "Cat is crying because you didn't complete the task!")
            second_reply = QMessageBox.question(self, "Cat Reminder",
                                                "Are you sure you didn't complete the task?",
                                                QMessageBox.Yes | QMessageBox.No)
            if second_reply == QMessageBox.Yes:
                self.cat_die()
            else:
                QTimer.singleShot(5000, self.reset_to_idle)
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
        # chat_action = menu.addAction("Chat with Cat")
        # wellness_action = menu.addAction("Wellness Advice")
        # increase_action = menu.addAction("Increase Size")
        # decrease_action = menu.addAction("Decrease Size")
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        # if action == chat_action:
        #     chat_dialog = ChatDialog(self)
        #     chat_dialog.exec_()
        # elif action == wellness_action:
        #     wellness_dialog = WellnessDialog(self)
        #     wellness_dialog.exec_()
        # elif action == increase_action:
        #     self.increase_size()
        # elif action == decrease_action:
        #     self.decrease_size()
        if action == quit_action:
            self.close()

    # def increase_size(self):
    #     # Increase current window size by 20%
    #     rect = self.geometry()
    #     new_width = int(rect.width() * 1.2)
    #     new_height = int(rect.height() * 1.2)
    #     screen_height = pyautogui.size().height
    #     self.setGeometry(0, screen_height - new_height, new_width, new_height)
    #     self.update_layout(new_width, new_height)

    # def decrease_size(self):
    #     # Decrease current window size by 20%
    #     rect = self.geometry()
    #     new_width = int(rect.width() * 0.8)
    #     new_height = int(rect.height() * 0.8)
    #     screen_height = pyautogui.size().height
    #     self.setGeometry(0, screen_height - new_height, new_width, new_height)
    #     self.update_layout(new_width, new_height)

    # def update_layout(self, new_width, new_height):
    #     # Update geometry of child widgets based on new window size
    #     self.background_label.setGeometry(0, 0, new_width, new_height)
    #     self.cat_label.setGeometry(0, 0, new_width, new_height)
    #     self.timer_label.setGeometry(0, new_height - 60, new_width, 20)
    #     self.status_label.setGeometry(0, new_height - 40, new_width, 20)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CatBreakReminder()
    sys.exit(app.exec_())
