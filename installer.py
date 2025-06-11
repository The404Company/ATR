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
        
        self.program_files = os.path.expandvars("%ProgramFiles%")
        self.install_dir = Path(self.program_files) / "ATR"
        self.appdata_dir = Path(os.getenv('APPDATA')) / "ATR"
        self.appdata_dir.mkdir(exist_ok=True)
        self.installed = self.check_installation()
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="ATR - Auto Text Replacer", font=("Helvetica", 14, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=300, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to install")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # Install/Update button
        self.install_button = ttk.Button(
            main_frame, 
            text="Update" if self.installed else "Install",
            command=self.install
        )
        self.install_button.grid(row=3, column=0, padx=5)
        
        # Uninstall button (only shown if installed)
        if self.installed:
            self.uninstall_button = ttk.Button(main_frame, text="Uninstall", command=self.uninstall)
            self.uninstall_button.grid(row=3, column=1, padx=5)
        
        # Post-install frame (hidden initially)
        self.post_install_frame = ttk.Frame(main_frame)
        self.post_install_frame.grid(row=4, column=0, columnspan=2, pady=20)
        self.post_install_frame.grid_remove()
        
        # Start ATR checkbox
        self.start_atr = tk.BooleanVar(value=True)
        self.start_checkbox = ttk.Checkbutton(
            self.post_install_frame,
            text="Start ATR",
            variable=self.start_atr
        )
        self.start_checkbox.grid(row=0, column=0, pady=5)
        
        # Finish button
        self.finish_button = ttk.Button(
            self.post_install_frame,
            text="Finish",
            command=self.finish
        )
        self.finish_button.grid(row=1, column=0, pady=5)

    def check_installation(self):
        return (self.install_dir / "atr.exe").exists()

    def uninstall(self):
        if messagebox.askyesno("Confirm Uninstall", "Are you sure you want to uninstall ATR?"):
            try:
                # Remove from startup
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS) as key:
                    try:
                        winreg.DeleteValue(key, "ATR")
                    except WindowsError:
                        pass
                
                # Delete installation directory
                if self.install_dir.exists():
                    os.remove(self.install_dir / "atr.exe")
                    self.install_dir.rmdir()
                
                messagebox.showinfo("Success", "ATR has been uninstalled.")
                self.root.quit()
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to uninstall: {str(e)}")

    def install(self):
        if self.installed and not messagebox.askyesno("Update ATR", 
            "ATR is already installed. Would you like to update it?"):
            return

        self.install_button["state"] = "disabled"
        if hasattr(self, 'uninstall_button'):
            self.uninstall_button["state"] = "disabled"

        try:
            # Remove existing installation if updating
            if self.installed:
                os.remove(self.install_dir / "atr.exe")

            # Download icon
            self.update_status("Downloading icon...", 5)
            icon_response = requests.get("https://raw.githubusercontent.com/The404Company/ATR/refs/heads/main/atr_logo.png")
            icon_path = self.appdata_dir / "atr_logo.png"
            with open(icon_path, "wb") as f:
                f.write(icon_response.content)

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
                f"--icon={icon_path}",
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
            self.post_install_frame.grid()
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 0)
            self.install_button["state"] = "normal"
            if hasattr(self, 'uninstall_button'):
                self.uninstall_button["state"] = "normal"
            return

    def finish(self):
        if self.start_atr.get():
            subprocess.Popen([str(self.install_dir / "atr.exe")])
        self.root.quit()

    def update_status(self, text, progress):
        self.status_label["text"] = text
        self.progress["value"] = progress
        self.root.update()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    installer = InstallerGUI()
    installer.run()
