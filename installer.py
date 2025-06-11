import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import sys
import winreg
import subprocess
from pathlib import Path
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

class InstallerGUI:
    def __init__(self):
        if not is_admin():
            if messagebox.askyesno("Admin Rights Required", 
                "This installer needs administrator privileges. Would you like to restart with admin rights?"):
                run_as_admin()
                sys.exit()
            else:
                sys.exit()

        self.root = tk.Tk()
        self.root.title("ATR Installer")
        self.root.geometry("400x300")
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="ATR - Auto Text Replacer", font=("Helvetica", 14, "bold"))
        title.grid(row=0, column=0, pady=(0, 20))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=300, mode='determinate')
        self.progress.grid(row=1, column=0, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to install")
        self.status_label.grid(row=2, column=0, pady=(0, 20))
        
        # Install button
        self.install_button = ttk.Button(main_frame, text="Install", command=self.install)
        self.install_button.grid(row=3, column=0)
        
    def update_status(self, text, progress):
        self.status_label["text"] = text
        self.progress["value"] = progress
        self.root.update()
        
    def install(self):
        self.install_button["state"] = "disabled"
        
        try:
            # Download latest atr.py
            self.update_status("Downloading latest version...", 10)
            response = requests.get("https://raw.githubusercontent.com/The404Company/ATR/refs/heads/main/atr.py")
            source_code = response.text
            
            temp_dir = Path(os.getenv('TEMP')) / "atr_installer"
            temp_dir.mkdir(exist_ok=True)
            
            # Save temporary atr.py
            self.update_status("Preparing files...", 30)
            temp_atr = temp_dir / "atr.py"
            with open(temp_atr, "w", encoding="utf-8") as f:
                f.write(source_code)
            
            # Install required packages
            self.update_status("Installing dependencies...", 50)
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pynput", "pyperclip", "pystray", "Pillow"])
            
            # Compile to exe
            self.update_status("Compiling...", 70)
            subprocess.run([
                "pyinstaller",
                "--noconfirm",
                "--onefile",
                "--windowed",
                str(temp_atr)
            ], cwd=temp_dir)
            
            # Install to Program Files
            self.update_status("Installing...", 90)
            program_files = os.path.expandvars("%ProgramFiles%")
            install_dir = Path(program_files) / "ATR"
            install_dir.mkdir(exist_ok=True)
            
            # Copy executable
            exe_path = temp_dir / "dist" / "atr.exe"
            installed_exe = install_dir / "atr.exe"
            exe_path.rename(installed_exe)
            
            # Add to startup
            startup_path = Path(os.getenv('APPDATA')) / r"Microsoft\Windows\Start Menu\Programs\Startup"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "ATR", 0, winreg.REG_SZ, str(installed_exe))
            
            self.update_status("Installation completed!", 100)
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 0)
            self.install_button["state"] = "normal"
            return
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    installer = InstallerGUI()
    installer.run()
