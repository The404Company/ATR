import json
import os
import threading
from pynput import keyboard
import pyperclip
import time
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

CONFIG_FILE = "replacements.json"

# --- Load/Save ---
def load_replacements():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_replacements(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
        self.create_widgets()

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

def main():
    replacements = load_replacements()
    replacer = AutoReplacer(replacements)
    replacer.start()

    root = tk.Tk()
    gui = ReplacementGUI(root, replacer)
    root.mainloop()

if __name__ == "__main__":
    threading.Thread(target=main).start()
