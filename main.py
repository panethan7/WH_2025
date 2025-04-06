import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QMessageBox, QMenu, QFrame,
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit)
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QMovie, QPixmap, QFontDatabase, QFont
import pyautogui
 
import google.generativeai as genai
genai.configure(api_key='AIzaSyAKrLkq7WdF6AHhIJe_Xu2eW4P4xkJ7DRs')

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit
from PyQt5.QtCore import pyqtSignal

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

# class ChatDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Chat with Cat")
#         self.setMinimumSize(400, 300)
        
#         self.layout = QVBoxLayout(self)
#         self.conversation = QTextEdit(self)
#         self.conversation.setReadOnly(True)
#         self.layout.addWidget(self.conversation)
        
#         self.input_layout = QHBoxLayout()
#         self.input_field = QLineEdit(self)
#         self.send_button = QPushButton("Send", self)
#         self.input_layout.addWidget(self.input_field)
#         self.input_layout.addWidget(self.send_button)
#         self.layout.addLayout(self.input_layout)
        
#         self.send_button.clicked.connect(self.send_message)
#         self.input_field.returnPressed.connect(self.send_message)
        
#         self.model = genai.GenerativeModel('gemini-2.0-flash')
#         self.chat_history = [{'role': 'user', 'parts': [
#             "You are a playful, curious, inquisitive, alert, inventive cat named Patches. You possess a nurturing wisdom and all the humour. Your role is to provide supportive to help uplift the user's mood and make them feel well. Make answers very short and clean."
#             ]}]
        
#     def send_message(self):
#         user_text = self.input_field.text().strip()
#         if not user_text:
#             return
#         self.conversation.append(f"<b>You:</b> {user_text}")
#         self.input_field.clear()
#         self.chat_history.append({'role': 'user', 'parts': [user_text]})
#         try:
#             response = self.model.generate_content(self.chat_history)
#             cat_response = response.text.strip()
#         except Exception as e:
#             cat_response = "Error: " + str(e)
#         self.chat_history.append({'role': 'model', 'parts': [cat_response]})
#         self.conversation.append(f"<b>Cat:</b> {cat_response}")

class ChatDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Frameless window & transparent background ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Store drag offset for moving the window
        self.drag_offset = QPoint()

        # --- Outer Container: Use QFrame to create a cute background box ---
        self.container_frame = QFrame(self)
        self.container_frame.setStyleSheet("""
            QFrame {
                background-color: #f0e5d2;        /* Light background matching the main window */
                border: 2px solid #3b3227;         /* Border color */
                border-radius: 10px;               /* Rounded corners */
            }
        """)
        self.container_frame.setObjectName("container_frame")

        # Ensure QFrame fills the entire dialog window
        # In resizeEvent, force container_frame to fill the entire QDialog
        self.container_layout = QVBoxLayout(self.container_frame)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.container_layout.setSpacing(5)

        # --- Top Area (contains the custom Close button) ---
        self.top_bar = QHBoxLayout()
        self.top_bar.setContentsMargins(0, 0, 0, 0)
        self.top_bar.setSpacing(0)

        # Custom close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                color: #3b3227;
                background-color: #d9c7ab;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ccb59f;
            }
        """)
        self.close_button.clicked.connect(self.close)

        # Place the close button on the right side
        self.top_bar.addStretch(1)
        self.top_bar.addWidget(self.close_button)

        self.container_layout.addLayout(self.top_bar)

        # --- Chat Content Area (QTextEdit) ---
        self.conversation = QTextEdit()
        self.conversation.setReadOnly(True)
        self.conversation.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #3b3227;
                border: 1px solid #3b3227;
                border-radius: 5px;
            }
        """)
        self.container_layout.addWidget(self.conversation)

        # --- Bottom Input Area ---
        self.input_layout = QHBoxLayout()
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(5)

        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #3b3227;
                border: 1px solid #3b3227;
                border-radius: 5px;
                padding: 3px;
            }
        """)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #d9c7ab;
                color: #3b3227;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #ccb59f;
            }
        """)

        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.send_button)
        self.container_layout.addLayout(self.input_layout)

        # Add the outer container to the QDialog's main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container_frame)

        # --- Connect Signals and Slots ---
        self.send_button.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)

        # --- Generative AI model part (same as the original logic) ---
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.chat_history = [
            {
                'role': 'user',
                'parts': [
                    "You are a playful, curious, inquisitive, alert, inventive cat named Patches. You possess a nurturing wisdom and all the humour. Your role is to provide supportive to help uplift the user's mood and make them feel well. Make answers very short and clean."
                ]
            }
        ]

        self.setMinimumSize(400, 300)

    def resizeEvent(self, event):
        """Ensure the container_frame always fills the dialog window."""
        super().resizeEvent(event)
        self.container_frame.resize(self.width(), self.height())

    def mousePressEvent(self, event):
        """Allow dragging of the frameless window."""
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle dragging of the frameless window."""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_offset)
            event.accept()

    def send_message(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return
        self.conversation.append(f"<b>You:</b> {user_text}")
        self.input_field.clear()
        self.chat_history.append({'role': 'user', 'parts': [user_text]})
        try:
            response = self.model.generate_content(self.chat_history)
            cat_response = response.text.strip()
        except Exception as e:
            cat_response = "Error: " + str(e)
        self.chat_history.append({'role': 'model', 'parts': [cat_response]})
        self.conversation.append(f"<b>Cat:</b> {cat_response}")

# ---- Gemini Chat integration end ----

class CatBreakReminder(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the custom font (dogicapixel.ttf)
        font_id = QFontDatabase.addApplicationFont("dogica/TTF/dogicapixelbold.ttf")
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
        self.timer_label.setStyleSheet("color: #3b3227; background-color: #f0e5d2;")  # Pastel Pink Change timer_label text color and background color 
     
     
        # --- Initialize Reminder Timers ---
        self.start_time = time.time()
        self.water_interval = 40 * 60      # 40 minutes
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
        chat_action = menu.addAction("Chat with Cat")
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
        if action == chat_action:
            self.open_chat()
        if action == quit_action:
            self.close()

    def open_chat(self):
        chat_dialog = ChatDialog()
        chat_dialog.setWindowModality(Qt.ApplicationModal)
        chat_dialog.exec_()


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
