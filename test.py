import tkinter as tk
import pyautogui

impath = 'sprites/'

window = tk.Tk()
window.overrideredirect(True)  # Removes window border
window.wm_attributes('-topmost', True)  # Keep it on top
window.attributes('-transparentcolor', 'black')  # Make black transparent

# Get screen size to place it at bottom-left
screen_width, screen_height = pyautogui.size()
window.geometry(f'100x100+0+{screen_height - 100}')

frames = [tk.PhotoImage(file=impath + 'idle1_5cm.gif', format='gif -index %i' % i) for i in range(10)]

label = tk.Label(window, bd=0, bg='black')
label.pack()

def update(ind):
  frame = frames[ind]
  label.configure(image=frame)
  ind = (ind + 1) % len(frames)
  window.after(100, update, ind)

window.after(0, update, 0)
window.mainloop()