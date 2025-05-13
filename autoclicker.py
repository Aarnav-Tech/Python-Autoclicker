import tkinter as tk
from tkinter import ttk, messagebox
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, Key
import threading
import time
import tkinter.font as tkfont
import os
import sys
import platform

# ======== Single Instance Lock =========
lock_file = None

def enforce_single_instance():
    global lock_file
    lock_path = os.path.join("/tmp" if platform.system() != "Windows" else os.environ["TEMP"], "autoclicker.lock")
    lock_file = open(lock_path, "w")

    try:
        if platform.system() == "Windows":
            import msvcrt
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Already Running", "Another instance of AutoClicker is already running.")
        sys.exit()

enforce_single_instance()

# ======== Main Autoclicker Logic =========
mouse = MouseController()
clicking = False
hotkey = Key.f6
hotkey_config = {
    "F6": Key.f6,
    "F7": Key.f7,
    "F8": Key.f8,
    "F9": Key.f9
}

def get_interval_seconds():
    try:
        hours = int(hour_var.get())
        minutes = int(min_var.get())
        seconds = int(sec_var.get())
        millis = int(ms_var.get())
        total = hours * 3600 + minutes * 60 + seconds + millis / 1000
        status_var.set("🛑 Idle" if not clicking else "✅ Clicking...")
        return total if total > 0 else 0.01
    except ValueError:
        status_var.set("❌ Invalid input")
        return None

def click_loop(button_type):
    global clicking
    while clicking:
        interval = get_interval_seconds()
        if interval is None: break
        btn = Button.left if button_type == 'Left' else Button.right
        mouse.click(btn)
        time.sleep(interval)

def toggle_clicking():
    global clicking
    button_type = button_var.get()
    if get_interval_seconds() is None:
        return
    clicking = not clicking
    if clicking:
        status_var.set("✅ Clicking...")
        start_button.config(text="🛑 Stop", style="Stop.TButton")
        threading.Thread(target=click_loop, args=(button_type,), daemon=True).start()
    else:
        status_var.set("🛑 Idle")
        start_button.config(text="▶ Start", style="Start.TButton")

def on_press(key):
    if key == hotkey:
        toggle_clicking()

listener = Listener(on_press=on_press)
listener.start()

# ======== GUI Setup =========
root = tk.Tk()
root.title("Autoclicker")
root.geometry("400x420")
root.configure(bg="#f0f2f5")
root.resizable(False, False)

style = ttk.Style()
style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 10))
style.configure("TCombobox", padding=5)
style.configure("Start.TButton", background="#4CAF50", foreground="white", font=("Segoe UI", 10, "bold"))
style.configure("Stop.TButton", background="#f44336", foreground="white", font=("Segoe UI", 10, "bold"))

main_frame = ttk.Frame(root, padding=20, relief="groove", borderwidth=2)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
ttk.Label(main_frame, text="Autoclicker", font=title_font).pack(pady=(0, 20))

# Interval Input
ttk.Label(main_frame, text="Click Interval").pack()
interval_frame = ttk.Frame(main_frame)
interval_frame.pack(pady=10)

def create_interval_input(label, var):
    frame = ttk.Frame(interval_frame)
    frame.pack(side=tk.LEFT, padx=5)
    entry = ttk.Entry(frame, textvariable=var, width=5, justify="center")
    entry.pack()
    ttk.Label(frame, text=label).pack()
    entry.bind("<Enter>", lambda e: status_var.set(f"Enter {label} value"))
    entry.bind("<Leave>", lambda e: status_var.set("🛑 Idle" if not clicking else "✅ Clicking..."))

hour_var = tk.StringVar(value="0")
min_var = tk.StringVar(value="0")
sec_var = tk.StringVar(value="0")
ms_var = tk.StringVar(value="100")

create_interval_input("hours", hour_var)
create_interval_input("mins", min_var)
create_interval_input("secs", sec_var)
create_interval_input("ms", ms_var)

# Mouse Button Selector
ttk.Label(main_frame, text="Mouse Button").pack()
button_var = tk.StringVar(value="Left")
button_menu = ttk.Combobox(main_frame, textvariable=button_var, values=["Left", "Right"], state="readonly", width=10)
button_menu.pack(pady=10)
button_menu.bind("<Enter>", lambda e: status_var.set("Select mouse button to click"))
button_menu.bind("<Leave>", lambda e: status_var.set("🛑 Idle" if not clicking else "✅ Clicking..."))

# Hotkey Selector
ttk.Label(main_frame, text="Hotkey").pack()
hotkey_var = tk.StringVar(value="F6")
def update_hotkey(event=None):
    global hotkey
    hotkey = hotkey_config[hotkey_var.get()]
hotkey_menu = ttk.Combobox(main_frame, textvariable=hotkey_var, values=list(hotkey_config.keys()), state="readonly", width=10)
hotkey_menu.bind("<<ComboboxSelected>>", update_hotkey)
hotkey_menu.pack(pady=10)
hotkey_menu.bind("<Enter>", lambda e: status_var.set("Select hotkey to toggle clicking"))
hotkey_menu.bind("<Leave>", lambda e: status_var.set("🛑 Idle" if not clicking else "✅ Clicking..."))

# Start/Stop Button
start_button = ttk.Button(main_frame, text="▶ Start", command=toggle_clicking, style="Start.TButton")
start_button.pack(pady=20)

# Status
status_var = tk.StringVar(value="🛑 Idle")
status_label = ttk.Label(main_frame, textvariable=status_var, foreground="#1565C0")
status_label.pack()

# Instruction
ttk.Label(main_frame, text="Use hotkey or button to toggle", font=("Segoe UI", 9)).pack(pady=10)

root.mainloop()
