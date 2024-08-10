import os
import json
import glob
import sys
import shutil
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from datetime import datetime

CONFIG_FILE_NAME = 'config.json'

def get_persistent_config_path():
    if sys.platform == "win32":
        appdata_dir = os.getenv('LOCALAPPDATA')
        config_dir = os.path.join(appdata_dir, "GTAW_ScreenSorter")
    else:
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, ".config", "GTAW_ScreenSorter")
    
    # Ensure the directory exists
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    return os.path.join(config_dir, CONFIG_FILE_NAME)

def get_config_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, CONFIG_FILE_NAME)
    else:
        return os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)

def load_config():
    config_path = get_persistent_config_path()
    print(f"Loading config from: {config_path}")

    default_config = {
        'folder_path': None
    }

    if not os.path.exists(config_path):
        print("Config file does not exist, creating a new one with defaults values.")
        save_config(default_config)
        return default_config

    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
            print(f"Config loaded: {config}")
            return config
    except json.JSONDecodeError as e:
        print(f"Error loading JSON: {e}. Creating a new config file with default values.")
        save_config(default_config)
        return default_config

def save_config(config):
    config_path = get_persistent_config_path()
    print(f"Saving config to: {config_path}")
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)
    print(f"Config saved: {config}")

def sort():
    if folder_path is None:
        messagebox.showerror("Error", "Folder path is not specified in the config file.")
        return

    print(f"Sorting files and folders in: {folder_path}")

    # Step 1: Sort PNG files directly in the main folder
    png_files = glob.glob(os.path.join(folder_path, '*.png'))
    print(f"PNG files found: {png_files}")

    date_pattern = re.compile(r'(\d{4})[-_/](\d{1,2})[-_/](\d{1,2})')
    errors = []

    if png_files:
        for file in png_files:
            base_name = os.path.basename(file)
            match = date_pattern.search(base_name)

            if match:
                # Extract the date from the filename
                year, month, day = match.groups()
                year = int(year)
                month = int(month)
                day = int(day)
            else:
                # No date found, use file creation date
                creation_time = os.path.getctime(file)
                creation_date = datetime.fromtimestamp(creation_time)
                year = creation_date.year
                month = creation_date.month
                day = creation_date.day

                # Rename the file to include the creation date
                new_base_name = f"{year}-{month:02d}-{day:02d}_{base_name}"
                new_file_path = os.path.join(folder_path, new_base_name)
                os.rename(file, new_file_path)
                print(f"File '{base_name}' renamed to '{new_base_name}' using its creation date.")
                file = new_file_path
                base_name = new_base_name

            # Create the Month/Year folder path
            month_year_folder_name = f"{int(year)}-{int(month):02d}"
            month_year_folder_path = os.path.join(folder_path, month_year_folder_name)

            # Create the destination date folder within the Month/Year folder
            date_folder_name = f"{int(year)}-{int(month):02d}-{int(day):02d}"
            destination_path = os.path.join(month_year_folder_path, date_folder_name)
            destination_file = os.path.join(destination_path, base_name)
            print(f"Moving file '{file}' to '{destination_file}'")

            try:
                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)

                # Ensure the destination file doesn't already exist
                count = 1
                new_destination_file = destination_file
                while os.path.exists(new_destination_file):
                    new_destination_file = os.path.join(destination_path, f"{os.path.splitext(base_name)[0]}_{count}.png")
                    count += 1

                shutil.copy2(file, new_destination_file)
                print(f"File copied from '{file}' to '{new_destination_file}' successfully.")

                # Optionally, remove the original file only if the copy was successful
                if os.path.exists(new_destination_file):
                    os.remove(file)

            except Exception as e:
                errors.append(f"Error moving file '{file}': {e}")
                print(f"Error: {e}")

    # Step 2: Sort already existing full-date folders
    date_folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f)) and date_pattern.match(f)]
    print(f"Date folders found: {date_folders}")

    for folder in date_folders:
        match = date_pattern.match(folder)
        if match:
            year, month, day = match.groups()
            year = int(year)
            month = int(month)
            day = int(day)

            # Create the Month/Year folder path
            month_year_folder_name = f"{year}-{month:02d}"
            month_year_folder_path = os.path.join(folder_path, month_year_folder_name)

            # Create the destination path for the date folder
            destination_path = os.path.join(month_year_folder_path, folder)
            source_path = os.path.join(folder_path, folder)
            print(f"Moving folder '{source_path}' to '{destination_path}'")

            try:
                if not os.path.exists(month_year_folder_path):
                    os.makedirs(month_year_folder_path)

                # Move the date folder into the Month/Year folder
                shutil.move(source_path, destination_path)
                print(f"Folder moved from '{source_path}' to '{destination_path}' successfully.")

            except Exception as e:
                errors.append(f"Error moving folder '{folder}': {e}")
                print(f"Error: {e}")

    if not png_files and not date_folders:
        messagebox.showinfo("Sort Complete", "No PNG files or date folders found to sort.")

    if errors:
        error_message = "\n".join(errors)
        messagebox.showerror("Sort Complete", f"Sorting completed with errors:\n{error_message}")
    else:
        messagebox.showinfo("Sort Complete", "All files and folders have been sorted successfully.")


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
style.map("TButton", background=[("active", "#0056b3")])

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

# Sort Button
sortButton = ttk.Button(main_frame, text="Sort", command=sort, style="TButton")
sortButton.pack(pady=(10, 0))

config = load_config()
folder_path = config.get("folder_path", None)
if folder_path:
    fileLabel.config(text=f"{folder_path}")
    print(f"Loaded folder path: {folder_path}")

root.mainloop()
