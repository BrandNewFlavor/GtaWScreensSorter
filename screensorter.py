import os
import json
import glob
import sys
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

CONFIG_FILE_NAME = 'config.json'

def get_config_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), CONFIG_FILE_NAME)
    else:
        return os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)

def load_config():
    config_path = get_config_path()
    print(f"Loading config from: {config_path}")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
                print(f"Config loaded: {config}")
                return config
        except json.JSONDecodeError as e:
            print(f"Error loading JSON: {e}")
            return {}
    else:
        print("Config file does not exist.")
    return {}

def save_config(config):
    config_path = get_config_path()
    print(f"Saving config to: {config_path}")
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)
    print(f"Config saved: {config}")


def sort():
    if folder_path is None:
        messagebox.showerror("Error", "Folder path is not specified in the config file.")
        return

    png_files = glob.glob(os.path.join(folder_path, '*.png'))

    if not png_files:
        messagebox.showinfo("Sort Complete", "No PNG files found in the specified folder.")
        return

    print("PNG files found:")
    errors = []
    for file in png_files:
        parts = os.path.basename(file).replace('.png', '').split('-')
        if len(parts) < 5:
            errors.append(f"Invalid file name format: {file}")
            continue

        try:
            year = int(parts[2])
            month = int(parts[3])
            day = int(parts[4])
        except ValueError as e:
            errors.append(f"Error parsing date from file name '{file}': {e}")
            continue

        folder_name = f"{year}-{month}-{day}"
        destination_path = os.path.join(folder_path, folder_name)

        try:
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)
        
            shutil.move(file, destination_path)
            print(f"File moved from '{file}' to '{destination_path}' successfully.")
        except Exception as e:
            errors.append(f"Error moving file '{file}': {e}")

    if errors:
        error_message = "\n".join(errors)
        messagebox.showerror("Sort Complete", f"Sorting completed with errors:\n{error_message}")
    else:
        messagebox.showinfo("Sort Complete", "All PNG files have been sorted successfully.")

def open_file():
    global folder_path
    folder_path = filedialog.askdirectory(title="Select a folder")
    if folder_path:
        fileLabel.config(text=f"{folder_path}")
        save_config({'folder_path': folder_path})
        print(f"Selected folder: {folder_path}")

# Create the main window
root = tk.Tk()
root.title("GTAW Screens Sorter")
root.geometry("400x150")

# Apply styles
style = ttk.Style()
style.theme_use("clam")

# Define Bootstrap-like styles
style.configure("TLabel", foreground="#495057", font=("Helvetica", 10))
style.configure("TEntry", foreground="#495057", font=("Helvetica", 10))
style.configure("TButton", background="#007bff", foreground="#ffffff", font=("Helvetica", 10, "bold"), padding=6)
style.map("TButton",
          background=[("active", "#0056b3")])

# Main frame to hold all widgets
main_frame = ttk.Frame(root, padding="20", style="TFrame")
main_frame.pack(expand=True, fill="both")

root.configure(background="#f8f9fa")

# Open Folder Button
folderButton = ttk.Button(main_frame, text="Select Folder", command=open_file, style="TButton")
folderButton.pack()

# File Label
fileLabel = ttk.Label(main_frame, text="No folder selected", style="TLabel")
fileLabel.pack()

# Search Button
sortButton = ttk.Button(main_frame, text="Sort", command=sort, style="TButton")
sortButton.pack(pady=(10, 0))


config = load_config()
folder_path = config.get("folder_path", None)
if folder_path:
    fileLabel.config(text=f"{folder_path}")
    print(f"Loaded folder path: {folder_path}")

root.mainloop()

# get_all_screens()
