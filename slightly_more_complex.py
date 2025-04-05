import tkinter as tk
import pyautogui
import time
from tkinter import messagebox

impath = 'sprites-test/'  # Path to sprite images

# Main window setup
window = tk.Tk()
window.title("Cat Break Reminder")
window.overrideredirect(True)  # Removes window border
window.wm_attributes('-topmost', True)  # Keep it on top

# Get screen size to place it at bottom-left
screen_width, screen_height = pyautogui.size()
window_width, window_height = 445, 404  # Slightly larger window
window.geometry(f'{window_width}x{window_height}+0+{screen_height - window_height}')

# Background setup
bg_image = tk.PhotoImage(file=impath + 'cat_house.png')
background = tk.Label(window, image=bg_image)
background.place(x=0, y=0, relwidth=1, relheight=1)

# Load cat sprites
idle_frames = [tk.PhotoImage(file=impath + 'idle.gif', format='gif -index %i' % i) for i in range(5)]
sleep_frames = [tk.PhotoImage(file=impath + 'sleep.gif', format='gif -index %i' % i) for i in range(3)]
drink_frames = [tk.PhotoImage(file=impath + 'idle_to_sleep.gif', format='gif -index %i' % i) for i in range(8)]
stretch_frames = [tk.PhotoImage(file=impath + 'walk_negative.gif', format='gif -index %i' % i) for i in range(8)]

# Current animation state
current_frames = idle_frames
animation_state = "idle"

# Cat label
cat_label = tk.Label(window, bd=0, bg='black')
cat_label.pack(pady=50)

# Timer variables
start_time = time.time()
water_interval = 40 * 60  # 40 minutes in seconds
eye_interval = 20 * 60    # 20 minutes in seconds
stretch_interval = 2 * 60 * 60  # 2 hours in seconds

# Status variables
last_water_time = start_time
last_eye_time = start_time
last_stretch_time = start_time

# Status label
status_text = tk.StringVar()
status_text.set("Cat is watching you work...")
status_label = tk.Label(window, textvariable=status_text, bg='white', fg='black')
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Timer indicator
timer_text = tk.StringVar()
timer_label = tk.Label(window, textvariable=timer_text, bg='white', fg='black')
timer_label.pack(side=tk.BOTTOM, fill=tk.X)

# Function to show notification and handle cat animation
def show_notification(message, animation_type):
    global animation_state, current_frames
    
    # Show notification
    result = messagebox.askquestion("Cat Reminder", message + "\n\nDid you complete this task?")
    
    # Update cat animation based on response and type
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
    
    return result

# Reset to idle animation
def reset_to_idle():
    global animation_state, current_frames
    animation_state = "idle"
    current_frames = idle_frames
    status_text.set("Cat is watching you work...")

# Function to check timers
def check_timers():
    global last_water_time, last_eye_time, last_stretch_time
    
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
    if current_frames and len(current_frames) > 0:  # Check if list exists and has items
        frame = current_frames[ind % len(current_frames)]  # Use modulo to prevent index errors
        cat_label.configure(image=frame)
        ind = (ind + 1) % len(current_frames)
    else:
        # If no frames, show a message
        cat_label.configure(text="No frames loaded", image="")
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

# Exit button
exit_button = tk.Button(window, text="×", command=window.destroy, bg='red', fg='white')
exit_button.place(x=window_width-20, y=0, width=20, height=20)

# Start timer check
window.after(1000, check_timers)

# Start animation
window.after(0, update_animation, 0)

# Start the application
window.mainloop()