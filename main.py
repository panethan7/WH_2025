import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QMessageBox, QMenu, QFrame, QDialog, QTextEdit, QDialog, QInputDialog,
                             QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QPushButton, QScrollArea, QDesktopWidget, QSizeGrip)
from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl, pyqtSignal, QEvent, QSettings
from PyQt5.QtGui import QMovie, QPixmap, QFontDatabase, QFont, QIcon
import pyautogui

import google.generativeai as genai
genai.configure(api_key='')

# ---------------------------
# Chat Window
# ---------------------------
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

        self.input_field.installEventFilter(self)

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

        default_font = self.conversation.font()
        self.chat_font_size = default_font.pointSize() if default_font.pointSize() > 0 else 10
        self.chat_font = QFont(default_font)
        self.chat_font.setPointSize(self.chat_font_size)
        self.conversation.setFont(self.chat_font)
        self.input_field.setFont(self.chat_font)
        
        self.input_layout.addWidget(self.send_button)
        self.container_layout.addLayout(self.input_layout)

        # Add the outer container to the QDialog's main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container_frame)

        # Size change
        self.size_grip = QSizeGrip(self)
        self.container_layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)

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
    
    def eventFilter(self, source, event):
        if source == self.input_field and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.send_message() 
                return True
        return super().eventFilter(source, event)

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

    def increase_font(self):
        self.chat_font_size += 1
        self.chat_font.setPointSize(self.chat_font_size)
        self.conversation.setFont(self.chat_font)
        self.input_field.setFont(self.chat_font)

    def decrease_font(self):
        if self.chat_font_size > 1:
            self.chat_font_size -= 1
            self.chat_font.setPointSize(self.chat_font_size)
            self.conversation.setFont(self.chat_font)
            self.input_field.setFont(self.chat_font)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        increase_action = menu.addAction("Increase Font")
        decrease_action = menu.addAction("Decrease Font")
        action = menu.exec_(event.globalPos())
        if action == increase_action:
            self.increase_font()
        elif action == decrease_action:
            self.decrease_font()

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

        self.size_grip = QSizeGrip(self)
        main_layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        
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

        # API Key
        settings = QSettings("MyCompany", "CatBreakReminder")
        stored_key = settings.value("api_key", "")
        if stored_key:
            genai.configure(api_key=stored_key)
     
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
        chat_action = menu.addAction("Chat with Cat")
        to_do = menu.addAction("To-Do List")
        # api_settings_menu = menu.addMenu("API Settings")
        # set_api_action = api_settings_menu.addAction("Set API Key")
        # delete_api_action = api_settings_menu.addAction("Delete API Key")
        minimize_action = menu.addAction("Minimize")
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quit_action:
            QApplication.instance().quit()
        elif action == to_do:
            self.open_todo_list()
        elif action == minimize_action:
            self.showMinimized()
        elif action == chat_action:
            self.open_chat()
        # elif action == set_api_action:
        #     self.open_api_key_dialog()
        # elif action == delete_api_action:
        #     self.delete_api_key()

    def open_todo_list(self):
        self.todo_window = ToDoListWidget()
        self.todo_window.show()

    def open_chat(self):
        settings = QSettings("MyCompany", "CatBreakReminder")
        stored_key = settings.value("api_key", "")
        if not stored_key or stored_key.strip() == "":
            QMessageBox.warning(self, "API Key Required",
                                "You must set an API key before using Chat with Cat.")
            return
        chat_dialog = ChatDialog()
        chat_dialog.setWindowModality(Qt.ApplicationModal)
        chat_dialog.exec_()
    
    # def open_api_key_dialog(self):
    #     new_key, ok = QInputDialog.getText(self, "Set API Key", "Enter your API key:")
    #     if ok and new_key:
    #         settings = QSettings("MyCompany", "CatBreakReminder")
    #         settings.setValue("api_key", new_key)
    #         genai.configure(api_key=new_key)
    #         QMessageBox.information(self, "API Key Set", "The API key has been updated.")

    # def delete_api_key(self):
    #     reply = QMessageBox.question(self, "Delete API Key",
    #                                 "Are you sure you want to delete the stored API key?",
    #                                 QMessageBox.Yes | QMessageBox.No)
    #     if reply == QMessageBox.Yes:
    #         settings = QSettings("MyCompany", "CatBreakReminder")
    #         settings.remove("api_key")
    #         genai.configure(api_key="")
    #         QMessageBox.information(self, "API Key Deleted", "The API key has been removed.")

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
