# main.py

import tkinter as tk
from tkinter import ttk, messagebox
from task_manager import TaskManager

def create_menu(root):
    """Create the menu bar for the main window."""
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Exit", command=root.quit)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Task Manager v1.0"))

def create_notebook(root, db_names):
    """Create a notebook with tabs for each database."""
    notebook = ttk.Notebook(root)
    notebook.grid(row=0, column=0, sticky='nsew')
    for db_name in db_names:
        frame = ttk.Frame(notebook)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        notebook.add(frame, text=db_name)
        TaskManager(frame, db_name)
    return notebook

def main():
    """Main function to set up the GUI application."""
    root = tk.Tk()
    root.title("Task Manager")
    root.geometry('1200x700')
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    create_menu(root)
    db_names = ["test", "test1", "test2", "test3"]
    create_notebook(root, db_names)

    root.mainloop()

if __name__ == "__main__":
    main()
