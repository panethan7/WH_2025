import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QMessageBox, QMenu, QFrame,
                             QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QPushButton, QScrollArea, QDesktopWidget)
from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl
from PyQt5.QtGui import QMovie, QPixmap, QFontDatabase, QFont, QIcon
import pyautogui

import google.generativeai as genai

# ---------------------------
# To‑Do List Item Widget
# ---------------------------
class ToDoItemWidget(QWidget):
    def __init__(self, task_text=""):
        super().__init__()
        # Set the fixed size for the entire widget
        self.setFixedSize(140, 30)
        
        # Create a horizontal layout for the checkbox, text, and delete button
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Apply the background style via stylesheet (without width/height)
        # self.setStyleSheet("""
        #     QWidget {
        #         background-color: #FFF4E2;
        #         border: 1px solid #ccc;
        #         border-radius: 10px;
        #         width: 220px;
        #         height: 30px;
        #     }
        # """)

        # Create the checkbox with custom style
        self.checkbox = QCheckBox(self)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #000;
                border-radius: 3px;
                background: #fff;
            }
            QCheckBox::indicator:checked {
                background: #4CAF50;
                border: 1px solid #000;
            }
        """)
        self.checkbox.toggled.connect(self.update_strikethrough)
        layout.addWidget(self.checkbox)
        
        # Create a QLineEdit for the task text
        self.task_line = QLineEdit(self)
        self.task_line.setPlaceholderText("New Task")
        self.task_line.setText(task_text)
        self.task_line.setStyleSheet("border: none; background: #FFF4E2; font-size: 14px;")
        layout.addWidget(self.task_line)
        
        # Create a delete button for the task
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6666;
                border: none;
                border-radius: 5px;
                color: white;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ff4d4d;
            }
        """)
        self.delete_button.clicked.connect(self.delete_self)
        layout.addWidget(self.delete_button)
    
    def update_strikethrough(self, checked):
        font = self.task_line.font()
        font.setStrikeOut(checked)
        self.task_line.setFont(font)
    
    def delete_self(self):
        parent_layout = self.parentWidget().layout()
        parent_layout.removeWidget(self)
        self.deleteLater()

# ---------------------------
# To‑Do List Window
# ---------------------------
class ToDoListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To‑Do List")
        self.resize(320, 480)
        # Remove the window icon
        self.setWindowIcon(QIcon())
        # Set the entire window background color (outer window)
        self.setStyleSheet("background-color: #AA7045;")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        
        # Main vertical layout for the entire window
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Container widget for the list items with the same background color as the outer window
        self.list_container = QWidget()
        self.list_container.setStyleSheet("""
            QWidget {
                background-color: #AA7045;
                border: 2px solid #dcd0b0;
            }
        """)
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setSpacing(10)
        self.list_layout.setContentsMargins(10, 10, 10, 10)
        self.list_layout.addStretch()  # Add stretch at the end to push items upward
        
        # Scroll area for the list items
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.list_container)
        main_layout.addWidget(self.scroll_area)
        
        # Plus button at the bottom to add a new task
        self.plus_button = QPushButton("+", self)
        self.plus_button.setFixedHeight(40)
        self.plus_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                border: 2px solid #dcd0b0;
                border-radius: 20px;
                background-color: #dcd0b0;
            }
            QPushButton:hover {
                background-color: #cfc0a0;
            }
        """)
        self.plus_button.clicked.connect(self.add_task)
        main_layout.addWidget(self.plus_button)
        
    def add_task(self):
        # Create a new to‑do item and insert it before the stretch
        item = ToDoItemWidget()
        count = self.list_layout.count()
        if count > 0:
            # Remove the stretch item (last item)
            self.list_layout.takeAt(count - 1)
        self.list_layout.addWidget(item)
        self.list_layout.addStretch()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        minimize_action = menu.addAction("Minimize")
        close_action = menu.addAction("Close")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == minimize_action:
            self.showMinimized()
        elif action == close_action:
            self.close()


# ---------------------------
# Main App (Cat Break Reminder)
# ---------------------------
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
        self.status_label.setFont(font)  # Apply custom font
        self.status_label.setStyleSheet("color: #3b3227; background-color: #f0e5d2;")  # change font and background colors
       
        # Timer label (above status)
        self.timer_label = QLabel(self)
        self.timer_label.setGeometry(0, window_height - 60, window_width, 20)
        self.timer_label.setStyleSheet("background-color: white; color: black;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setText("Water: --m | Eyes: --m | Stretch: --m")
        self.timer_label.setFont(font)  # Apply custom font
        self.timer_label.setStyleSheet("color: #3b3227; background-color: #f0e5d2;")  # Pastel Pink, also wtf is this parameter
     
     
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
                    }
                    QPushButton:pressed {
                        background-color: #5E81AC;
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
        to_do = menu.addAction("To-Do List")
        minimize_action = menu.addAction("Minimize")
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quit_action:
            QApplication.instance().quit()
        elif action == to_do:
            self.open_todo_list()
        elif action == minimize_action:
            self.showMinimized()

    def open_todo_list(self):
        self.todo_window = ToDoListWidget()
        self.todo_window.show()

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
