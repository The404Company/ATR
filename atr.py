import json
import os
import threading
from pynput import keyboard
import pyperclip
import time
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import sys
from pathlib import Path
import pystray
from PIL import Image
import subprocess

def get_app_dir():
    if getattr(sys, 'frozen', False):
        # If compiled with PyInstaller
        app_dir = Path(os.path.expandvars(r'%APPDATA%\ATR'))
    else:
        # If running from source
        app_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

CONFIG_FILE = get_app_dir() / "replacements.json"

# --- Load/Save ---
def load_replacements():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_replacements(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_config_path():
    return get_app_dir() / "config.json"

def load_config():
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {"start_minimized": False}

def save_config(config):
    with open(get_config_path(), 'w') as f:
        json.dump(config, f)

# --- Global Replacer ---
class AutoReplacer:
    def __init__(self, replacements):
        self.replacements = replacements
        self.buffer = ""
        self.listener = keyboard.Listener(on_press=self.on_key)
        self.controller = keyboard.Controller()

    def start(self):
        self.listener.start()

    def on_key(self, key):
        try:
            char = key.char
        except AttributeError:
            if key == keyboard.Key.space:
                self.check_replacement()
                self.buffer = ""
            elif key == keyboard.Key.backspace:
                self.buffer = self.buffer[:-1]
            return
        self.buffer += char

    def check_replacement(self):
        for trigger, replacement in self.replacements.items():
            if self.buffer == trigger:  
                for _ in range(len(self.buffer) + 1):
                    self.controller.press(keyboard.Key.backspace)
                    self.controller.release(keyboard.Key.backspace)
                for char in replacement:
                    self.controller.press(char)
                    self.controller.release(char)
                self.controller.press(keyboard.Key.space)
                self.controller.release(keyboard.Key.space)
                return

# --- GUI ---
class ReplacementGUI:
    def __init__(self, root, replacer):
        self.root = root
        self.replacer = replacer
        self.replacements = load_replacements()
        self.replacer.replacements = self.replacements
        self.config = load_config()

        # Set window icon
        icon_path = Path(os.path.expandvars(r'%APPDATA%\ATR\atr_logo.ico'))
        if icon_path.exists():
            self.root.iconbitmap(icon_path)

        self.create_widgets()
        self.setup_tray()
        
        if getattr(sys, 'frozen', False) and self.config.get("start_minimized", False):
            self.root.withdraw()

    def create_widgets(self):
        self.root.title("Auto Text Replacer")
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.listbox = tk.Listbox(self.frame, width=40)
        self.listbox.pack()

        self.update_listbox()

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add", command=self.add_entry).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Edit", command=self.edit_entry).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_entry).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Save", command=self.save).grid(row=0, column=3, padx=5)

        bottom_frame = tk.Frame(self.frame)
        bottom_frame.pack(pady=5)

        tk.Button(bottom_frame, text="Open ATR Folder", 
                 command=self.open_app_dir).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Minimize to Tray", 
                 command=self.minimize_to_tray).pack(side=tk.LEFT, padx=5)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for k, v in self.replacements.items():
            self.listbox.insert(tk.END, f"{k} → {v}")

    def add_entry(self):
        trigger = simpledialog.askstring("Trigger", "Text to trigger replacement (without space):")
        if not trigger:
            return
        if " " in trigger:
            messagebox.showerror("Error", "Do not include spaces in trigger.")
            return
        replacement = simpledialog.askstring("Replacement", f"Replacement for '{trigger} ':")
        if replacement:
            self.replacements[trigger] = replacement
            self.update_listbox()

    def edit_entry(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        selected = list(self.replacements.keys())[selection[0]]
        new_trigger = simpledialog.askstring("Edit Trigger", "Edit trigger:", initialvalue=selected)
        new_replacement = simpledialog.askstring("Edit Replacement", "Edit replacement:", initialvalue=self.replacements[selected])
        if new_trigger and new_replacement:
            del self.replacements[selected]
            self.replacements[new_trigger] = new_replacement
            self.update_listbox()

    def delete_entry(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        key = list(self.replacements.keys())[selection[0]]
        del self.replacements[key]
        self.update_listbox()

    def save(self):
        save_replacements(self.replacements)
        self.replacer.replacements = self.replacements
        messagebox.showinfo("Saved", "Replacements saved.")

    def setup_tray(self):
        icon_path = Path(os.path.expandvars(r'%APPDATA%\ATR\atr_logo.ico'))
        try:
            self.icon = pystray.Icon(
                "ATR",
                Image.open(icon_path),
                "ATR",
                menu=pystray.Menu(
                    pystray.MenuItem("Show", self.show_window),
                    pystray.MenuItem("Exit", self.quit_app)
                )
            )
            threading.Thread(target=self.icon.run, daemon=True).start()
        except Exception:
            # Fallback to default black icon if loading fails
            icon_image = Image.new('RGB', (64, 64), 'black')
            self.icon = pystray.Icon(
                "ATR",
                icon_image,
                "ATR",
                menu=pystray.Menu(
                    pystray.MenuItem("Show", self.show_window),
                    pystray.MenuItem("Exit", self.quit_app)
                )
            )
            threading.Thread(target=self.icon.run, daemon=True).start()

    def minimize_to_tray(self):
        self.root.withdraw()
        self.config["start_minimized"] = True
        save_config(self.config)

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.config["start_minimized"] = False
        save_config(self.config)

    def quit_app(self):
        self.icon.stop()
        self.root.quit()

    def open_app_dir(self):
        app_dir = get_app_dir()
        if sys.platform == 'win32':
            subprocess.run(['explorer', str(app_dir)])

def main():
    replacements = load_replacements()
    replacer = AutoReplacer(replacements)
    replacer.start()

    root = tk.Tk()
    gui = ReplacementGUI(root, replacer)
    
    def on_closing():
        if getattr(sys, 'frozen', False):
            gui.minimize_to_tray()
        else:
            root.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    threading.Thread(target=main).start()
