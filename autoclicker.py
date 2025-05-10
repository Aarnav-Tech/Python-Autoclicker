import tkinter as tk
from tkinter import ttk
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, Key
import threading
import time
import os
import sys
import msvcrt #Windows only....

lock_file = None #Windows only....

#Windows only....
def enforce_single_instance():
    global lock_file
    lock_path = os.path.join(os.environ["TEMP"], "autoclicker.lock")
    lock_file = open(lock_path, "w")
    try:
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        print("Another instance is already running.")
        sys.exit()


mouse = MouseController()
clicking = False
hotkey = Key.f6

hotkey_options = {
    "F6": Key.f6,
    "F7": Key.f7,
    "F8": Key.f8,
    "F9": Key.f9
}

# --- GUI Setup ---
enforce_single_instance() #Windows Only.....
root = tk.Tk()
root.title("Autoclicker")
root.geometry("400x400")
root.configure(bg="#f0f2f5")
root.resizable(False, False)

status_var = tk.StringVar(value="🛑 Idle")

def get_interval():
    try:
        h = int(hour_var.get())
        m = int(min_var.get())
        s = int(sec_var.get())
        ms = int(ms_var.get())
        total = h * 3600 + m * 60 + s + ms / 1000
        return max(total, 0.01)
    except ValueError:
        status_var.set("❌ Invalid interval")
        return None

def click_loop(btn_type):
    global clicking
    while clicking:
        interval = get_interval()
        if interval is None:
            break
        mouse.click(Button.left if btn_type == "Left" else Button.right)
        time.sleep(interval)

def toggle_clicking():
    global clicking
    interval = get_interval()
    if interval is None:
        return
    clicking = not clicking
    update_ui()
    if clicking:
        btn_type = button_var.get()
        threading.Thread(target=click_loop, args=(btn_type,), daemon=True).start()

def update_ui():
    if clicking:
        start_btn.config(text="🛑 Stop", style="Stop.TButton")
        status_var.set("✅ Clicking...")
    else:
        start_btn.config(text="▶ Start", style="Start.TButton")
        status_var.set("🛑 Idle")

def on_hotkey_press(key):
    if key == hotkey:
        toggle_clicking()

listener = Listener(on_press=on_hotkey_press)
listener.start()

# --- Styles ---
style = ttk.Style()
style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 10))
style.configure("TEntry", font=("Segoe UI", 10))
style.configure("Start.TButton", background="#4CAF50", foreground="white")
style.configure("Stop.TButton", background="#f44336", foreground="white")

# --- Variables ---
hour_var = tk.StringVar(value="0")
min_var = tk.StringVar(value="0")
sec_var = tk.StringVar(value="0")
ms_var = tk.StringVar(value="100")
button_var = tk.StringVar(value="Left")
hotkey_var = tk.StringVar(value="F6")

def update_hotkey(event=None):
    global hotkey
    hotkey = hotkey_options[hotkey_var.get()]

# --- Layout ---
main = ttk.Frame(root, padding=20)
main.pack(fill="both", expand=True)

ttk.Label(main, text="Autoclicker", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

ttk.Label(main, text="Click Interval").pack()
interval_frame = ttk.Frame(main)
interval_frame.pack(pady=10)

def add_time_input(label, var):
    f = ttk.Frame(interval_frame)
    f.pack(side="left", padx=5)
    ttk.Entry(f, textvariable=var, width=5).pack()
    ttk.Label(f, text=label).pack()

add_time_input("h", hour_var)
add_time_input("m", min_var)
add_time_input("s", sec_var)
add_time_input("ms", ms_var)

ttk.Label(main, text="Mouse Button").pack(pady=(10, 0))
ttk.Combobox(main, textvariable=button_var, values=["Left", "Right"], state="readonly").pack()

ttk.Label(main, text="Hotkey").pack(pady=(10, 0))
hotkey_box = ttk.Combobox(main, textvariable=hotkey_var, values=list(hotkey_options.keys()), state="readonly")
hotkey_box.pack()
hotkey_box.bind("<<ComboboxSelected>>", update_hotkey)

start_btn = ttk.Button(main, text="▶ Start", command=toggle_clicking, style="Start.TButton")
start_btn.pack(pady=20)

ttk.Label(main, textvariable=status_var, foreground="#1565C0").pack()
ttk.Label(main, text="Use hotkey or Start button to toggle").pack(pady=10)

# Default hotkey setup
update_hotkey()

root.mainloop()
