import tkinter as tk
import pyautogui
import time
from tkinter import messagebox

impath = 'sprites-test/'  # Path to sprite images

# Define the transparency color (bright green)
TRANSPARENT_COLOR = "#17f900"  # RGB value for pure green

# Global flag for cat death
cat_dead = False

# Main window setup
window = tk.Tk()
window.title("Cat Break Reminder")
window.overrideredirect(True)  # Removes window border
window.wm_attributes('-topmost', True)  # Keep it on top
window.config(bg=TRANSPARENT_COLOR)  # Set background to our transparent color
window.attributes("-transparentcolor", TRANSPARENT_COLOR)  # Make this color transparent

# Get screen size to place it at bottom-left
screen_width, screen_height = pyautogui.size()
window_width, window_height = 445, 404
window.geometry(f'{window_width}x{window_height}+0+{screen_height - window_height}')

# Background setup - use a frame with the house image
bg_frame = tk.Frame(window)
bg_frame.place(x=0, y=0, width=window_width, height=window_height)

bg_image = tk.PhotoImage(file=impath + 'cat_house.png')
bg_label = tk.Label(bg_frame, image=bg_image, bd=0)
bg_label.place(x=0, y=0)

# Load cat sprites
idle_frames = [tk.PhotoImage(file=impath + 'idle1.gif', format='gif -index %i' % i) for i in range(5)]
sleep_frames = [tk.PhotoImage(file=impath + 'sleep.gif', format='gif -index %i' % i) for i in range(3)]
drink_frames = [tk.PhotoImage(file=impath + 'idle_to_sleep.gif', format='gif -index %i' % i) for i in range(8)]
stretch_frames = [tk.PhotoImage(file=impath + 'walk_negative.gif', format='gif -index %i' % i) for i in range(8)]
cry_frames = [tk.PhotoImage(file=impath + 'walk_positive.gif', format='gif -index %i' % i) for i in range(3)]
dead_image = tk.PhotoImage(file=impath + 'DeadCat.png')

# Current animation state
current_frames = idle_frames
animation_state = "idle"

# Cat label - set background to transparent color
cat_label = tk.Label(window, bd=0, bg=TRANSPARENT_COLOR)
cat_label.place(relx=0.5, rely=0.4, anchor="center")  # Position in the middle-upper area

# Timer variables
start_time = time.time()
water_interval = 40 * 60  # 40 minutes in seconds
eye_interval = 0.25 * 60    # 20 minutes in seconds
stretch_interval = 2 * 60 * 60  # 2 hours in seconds

# Status variables
last_water_time = start_time
last_eye_time = start_time
last_stretch_time = start_time

# Create a frame for UI elements (not transparent)
ui_frame = tk.Frame(window)
ui_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Status label
status_text = tk.StringVar()
status_text.set("Cat is watching you work...")
status_label = tk.Label(ui_frame, textvariable=status_text, bg='white', fg='black')
status_label.pack(fill=tk.X)

# Timer indicator
timer_text = tk.StringVar()
timer_label = tk.Label(ui_frame, textvariable=timer_text, bg='white', fg='black')
timer_label.pack(fill=tk.X)

def cat_die():
    """Set the cat to a dead state, show the dead image, and stop animations/timers."""
    global cat_dead, animation_state
    cat_dead = True
    animation_state = "dead"
    status_text.set("The cat has died. RIP.")
    cat_label.config(image=dead_image)

# Function to show notification and handle cat animation
def show_notification(message, animation_type):
    global animation_state, current_frames, last_water_time, last_eye_time, last_stretch_time

    result = messagebox.askquestion("Cat Reminder", message + "\n\nDid you complete this task?")
    
    if result == 'yes':
        if animation_type == "water":
            animation_state = "drink"
            current_frames = drink_frames
            status_text.set("Cat is drinking water!")
        elif animation_type == "eye":
            animation_state = "sleep"
            current_frames = sleep_frames
            status_text.set("Cat is napping while you rest your eyes!")
        elif animation_type == "stretch":
            animation_state = "stretch"
            current_frames = stretch_frames
            status_text.set("Cat is stretching with you!")
        
        # Reset to idle after 5 seconds
        window.after(5000, reset_to_idle)
    
    elif result == 'no':
        # Start crying animation and ask for confirmation
        animation_state = "cry"
        current_frames = cry_frames
        status_text.set("Cat is crying because you didn't complete the task!")
        second_result = messagebox.askquestion("Cat Reminder", "Are you sure you didn't complete the task?")
        if second_result == 'no':
            # Cat dies if user confirms they really didn't complete the task
            cat_die()
            return second_result
        else:
            # If the user changes their mind, reset after 5 seconds
            window.after(5000, reset_to_idle)
    
    return result

# Reset to idle animation
def reset_to_idle():
    global animation_state, current_frames
    if not cat_dead:
        animation_state = "idle"
        current_frames = idle_frames
        status_text.set("Cat is watching you work...")

# Function to check timers
def check_timers():
    global last_water_time, last_eye_time, last_stretch_time

    # Stop timer checks if the cat is dead
    if cat_dead:
        return
    
    current_time = time.time()
    
    # Water reminder (40 minutes)
    if current_time - last_water_time >= water_interval:
        result = show_notification("Time to drink some water!", "water")
        if result == 'yes':
            last_water_time = current_time
    
    # Eye break reminder (20 minutes)
    if current_time - last_eye_time >= eye_interval:
        result = show_notification("Time to take an eye break! Look at something far away for 20 seconds.", "eye")
        if result == 'yes':
            last_eye_time = current_time
    
    # Stretch reminder (2 hours)
    if current_time - last_stretch_time >= stretch_interval:
        result = show_notification("Time to take a stretch break!", "stretch")
        if result == 'yes':
            last_stretch_time = current_time
    
    # Update timer display
    update_timer_display(current_time)
    
    # Schedule next check in 1 second
    window.after(1000, check_timers)

# Update timer display
def update_timer_display(current_time):
    water_remaining = water_interval - (current_time - last_water_time)
    eye_remaining = eye_interval - (current_time - last_eye_time)
    stretch_remaining = stretch_interval - (current_time - last_stretch_time)
    
    timer_text.set(f"Water: {int(water_remaining/60)}m | Eyes: {int(eye_remaining/60)}m | Stretch: {int(stretch_remaining/60)}m")

# Function to update animation frames
def update_animation(ind):
    if cat_dead:
        # Stop animation updates if the cat is dead.
        return

    if current_frames and len(current_frames) > 0:
        frame = current_frames[ind % len(current_frames)]
        cat_label.config(image=frame)
        ind = (ind + 1) % len(current_frames)
    else:
        cat_label.config(text="No frames loaded", image="")
        status_text.set("Error: No animation frames found!")
    
    # Schedule next animation update
    window.after(150, update_animation, ind)

# Make window draggable
def start_drag(event):
    window.x = event.x
    window.y = event.y

def stop_drag(event):
    window.x = None
    window.y = None

def drag(event):
    deltax = event.x - window.x
    deltay = event.y - window.y
    x = window.winfo_x() + deltax
    y = window.winfo_y() + deltay
    window.geometry(f"+{x}+{y}")

window.bind("<ButtonPress-1>", start_drag)
window.bind("<ButtonRelease-1>", stop_drag)
window.bind("<B1-Motion>", drag)

# Create a right-click (context) menu
right_click_menu = tk.Menu(window, tearoff=0)
right_click_menu.add_command(label="Quit", command=window.destroy)

def show_right_click_menu(event):
    right_click_menu.tk_popup(event.x_root, event.y_root)

# Bind right-click (Button-3 is right click on most systems)
window.bind("<Button-3>", show_right_click_menu)

# Start timer check
window.after(1000, check_timers)

# Start animation
window.after(0, update_animation, 0)

# Start the application
window.mainloop()
