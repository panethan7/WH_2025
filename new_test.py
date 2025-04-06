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
        self.screen_width, self.screen_height = pyautogui.size()
        
        # ===== MODIFIABLE RATIOS: Window size relative to screen =====
        self.window_width_ratio = 0.22  # Window width as percentage of screen width
        self.window_height_ratio = 0.42  # Window height as percentage of screen height
        # =============================================================
        
        # Calculate actual window dimensions based on screen size and ratios
        self.base_window_width = int(self.screen_width * self.window_width_ratio)
        self.base_window_height = int(self.screen_height * self.window_height_ratio)
        self.window_width, self.window_height = self.base_window_width, self.base_window_height
        
        # Position window at bottom of screen
        self.setGeometry(0, self.screen_height - self.window_height, self.window_width, self.window_height)

        # ===== MODIFIABLE RATIOS: Cat position within window =====
        self.cat_x_ratio = 0.36  # Cat x-position as percentage of window width
        #self.cat_x_ratio = 0.50  # Cat x-position as percentage of window width

        #this
        self.cat_y_ratio = 0.50  # Cat y-position as percentage of window height
        # ======================================================
        
        # ===== MODIFIABLE RATIOS: House position =====
        self.house_x_ratio = 0.5  # House x-position as percentage of window width
        self.house_y_ratio = 0.5  # House y-position as percentage of window height
        #self.house_x_ratio = 0.22  # House x-position as percentage of window width
        #self.house_y_ratio = 0.42  # House y-position as percentage of window height

        # ==============================================

        # ===== NEW: Cat size relative to window =====
        self.cat_width_ratio = 0.30  # Cat width as percentage of window width
        self.cat_height_ratio = 0.30  # Cat height as percentage of window height
        # ============================================

        # ===== NEW: House size relative to window =====
        self.house_width_ratio = 0.5  # House width as percentage of window width
        self.house_height_ratio = 0.5  # House height as percentage of window height
        # ==============================================

        # Calculate actual cat position based on window size and ratios
        self.base_cat_x = int(self.base_window_width * self.cat_x_ratio)
        self.base_cat_y = int(self.base_window_height * self.cat_y_ratio)
        self.cat_x, self.cat_y = self.base_cat_x, self.base_cat_y

        # Calculate base cat size
        self.base_cat_width = int(self.base_window_width * self.cat_width_ratio)
        self.base_cat_height = int(self.base_window_height * self.cat_height_ratio)
        self.cat_width, self.cat_height = self.base_cat_width, self.base_cat_height

        # Calculate house position based on window size and ratios
        self.base_house_x = int(self.base_window_width * self.house_x_ratio)
        self.base_house_y = int(self.base_window_height * self.house_y_ratio)
        self.house_x, self.house_y = self.base_house_x, self.base_house_y

        # Calculate base house size
        self.base_house_width = int(self.base_window_width * self.house_width_ratio)
        self.base_house_height = int(self.base_window_height * self.house_height_ratio)
        self.house_width, self.house_height = self.base_house_width, self.base_house_height

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
        self.background_label.setGeometry(0, 0, self.window_width, self.window_height)
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)

        # Cat label: displays the animated cat
        self.cat_label = QLabel(self)
        self.cat_label.setGeometry(self.cat_x, self.cat_y, self.cat_width, self.cat_height)
        self.cat_label.setStyleSheet("background-color: transparent;")
        self.cat_label.setScaledContents(True)  # Enable scaling for cat animations
        # Start with the idle animation
        self.current_movie = self.movie_idle
        self.cat_label.setMovie(self.current_movie)
        self.current_movie.start()

        # House label: displays the house
        self.house_label = QLabel(self)
        self.house_label.setGeometry(self.house_x, self.house_y, self.house_width, self.house_height)
        self.house_label.setStyleSheet("background-color: transparent;")
        self.house_label.setPixmap(QPixmap('sprites/house.png'))  # Assume there's a house image
        self.house_label.setScaledContents(True)

        # ===== MODIFIABLE RATIOS: Status label positions =====
        self.status_height_ratio = 0.05  # Status height as percentage of window height
        self.timer_offset_ratio = 0.05   # Timer position offset from status as percentage of window height
        # ==================================================

        # Status label (at the bottom)
        status_height = int(self.window_height * self.status_height_ratio)
        self.status_label = QLabel(self)
        self.status_label.setGeometry(0, self.window_height - status_height, self.window_width, status_height)
        self.status_label.setStyleSheet("background-color: white; color: black;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setText("Cat is watching you work...")
        self.status_label.setFont(font)  # Apply custom font
        self.status_label.setStyleSheet("color: #3b3227; background-color: #f0e5d2;")  # change font and background colors
       
        # Timer label (above status)
        timer_offset = int(self.window_height * self.timer_offset_ratio)
        self.timer_label = QLabel(self)
        self.timer_label.setGeometry(0, self.window_height - status_height - timer_offset, self.window_width, status_height)
        self.timer_label.setStyleSheet("background-color: white; color: black;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setText("Water: --m | Eyes: --m | Stretch: --m")
        self.timer_label.setFont(font)  # Apply custom font
        self.timer_label.setStyleSheet("color: #3b3227; background-color: #f0e5d2;")  # Pastel Pink
     
        # ===== MODIFIABLE INTERVALS: Reminder timers =====
        self.water_interval = 40 * 60      # 40 minutes
        self.eye_interval = 20 * 60        # 20 minutes (currently set to 0.1 for testing)
        self.stretch_interval = 2 * 60 * 60 # 2 hours
        # =============================================

        # --- Initialize Reminder Timers ---
        self.start_time = time.time()
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

        # Track current zoom level (1.0 = original size)
        self.zoom_level = 1.0

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
        self.cat_label.setPixmap(self.dead_pixmap.scaled(self.cat_width, self.cat_height, Qt.KeepAspectRatio))
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
        increase_action = menu.addAction("Zoom In")
        decrease_action = menu.addAction("Zoom Out")
        reset_zoom_action = menu.addAction("Reset Zoom")
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == increase_action:
            self.increase_size()
        elif action == decrease_action:
            self.decrease_size()
        elif action == reset_zoom_action:
            self.reset_zoom()
        elif action == quit_action:
            self.close()

    def increase_size(self):
        # Increase current window size by 20%
        self.zoom_level *= 1.2
        self.update_size()

    def decrease_size(self):
        # Decrease current window size by 20%
        self.zoom_level *= 0.8
        self.update_size()
        
    def reset_zoom(self):
        # Reset to original size
        self.zoom_level = 1.0
        self.update_size()

    def update_size(self):
        # Compute new dimensions based on zoom level
        new_width = int(self.base_window_width * self.zoom_level)
        new_height = int(self.base_window_height * self.zoom_level)
        
        # Update window size and position
        self.window_width, self.window_height = new_width, new_height
        self.setGeometry(0, self.screen_height - new_height, new_width, new_height)
        
        # Update layout components (including cat and house sizes)
        self.update_layout()
        
    def update_layout(self):
        # Update geometry of child widgets based on new window size
        self.background_label.setGeometry(0, 0, self.window_width, self.window_height)
        
        # Calculate new cat dimensions and position based on zoom level
        self.cat_x = int(self.window_width * self.cat_x_ratio)
        self.cat_y = int(self.window_height * self.cat_y_ratio)
        self.cat_width = int(self.window_width * self.cat_width_ratio)
        self.cat_height = int(self.window_height * self.cat_height_ratio)
        
        # Update cat label position and size
        self.cat_label.setGeometry(self.cat_x, self.cat_y, self.cat_width, self.cat_height)
        
        # Calculate new house dimensions and position based on zoom level
        self.house_x = int(self.window_width * self.house_x_ratio)
        self.house_y = int(self.window_height * self.house_y_ratio)
        self.house_width = int(self.window_width * self.house_width_ratio)
        self.house_height = int(self.window_height * self.house_height_ratio)
        
        # Update house label position and size
        self.house_label.setGeometry(self.house_x, self.house_y, self.house_width, self.house_height)
        
        # If cat is dead, rescale the dead cat pixmap
        if self.cat_dead:
            self.cat_label.setPixmap(self.dead_pixmap.scaled(self.cat_width, self.cat_height, Qt.KeepAspectRatio))
        
        # Update bottom status labels using ratios
        status_height = int(self.window_height * self.status_height_ratio)
        timer_offset = int(self.window_height * self.timer_offset_ratio)
        
        self.timer_label.setGeometry(0, self.window_height - status_height - timer_offset, self.window_width, status_height)
        self.status_label.setGeometry(0, self.window_height - status_height, self.window_width, status_height)
        
        # Update font size based on zoom
        current_font = self.status_label.font()
        new_font_size = max(6, int(6 * self.zoom_level))  # Minimum size of 6
        current_font.setPointSize(new_font_size)
        
        self.status_label.setFont(current_font)
        self.timer_label.setFont(current_font)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CatBreakReminder()
    sys.exit(app.exec_())