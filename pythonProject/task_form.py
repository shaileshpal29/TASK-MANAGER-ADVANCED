# task_form.py

import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import create_label, create_entry, create_text, create_combobox, create_button


class TaskForm(tk.Toplevel):
    def __init__(self, parent, task_manager, db, values=None, selected_item=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.db = db
        self.values = values
        self.selected_item = selected_item
        self.create_widgets()
        self.populate_fields()

    def create_widgets(self):
        self.title("Task Form")
        self.geometry('730x610')
        self.configure(bg='lightgrey')
        self.entries = {}

        labels = [
            "Assigned Date (YYYY-MM-DD)", "Task", "Status", "Completion Date (YYYY-MM-DD)",
            "Issue", "Remark", "Test Result Path", "Assigned To", "Priority", "Progress percentage"
        ]

        for i, label in enumerate(labels):
            create_label(self, label, i, 0)
            if label in ("Remark", "Issue"):
                entry = create_text(self, i, 1)
                entry.bind('<KeyRelease>', self.adjust_text_height)
            elif label == "Status":
                status_options = ["Done", "Pending", "Descoped", "Blocker", "Inprogress"]
                if self.values:
                    status_options.append("Closed")
                entry = create_combobox(self, i, 1, status_options)
            else:
                entry = create_entry(self, i, 1)
                entry.bind('<KeyRelease>', self.adjust_entry_width)
            self.entries[label] = entry

        save_button = create_button(self, "Save", self.save_task, len(labels), 0, columnspan=2)
        self.style_buttons()

    def adjust_entry_width(self, event):
        entry = event.widget
        text_length = len(entry.get())
        max_width = 50
        entry.config(width=min(text_length + 1, max_width))

    def adjust_text_height(self, event):
        text_widget = event.widget
        content = text_widget.get("1.0", "end-1c")
        lines = content.split('\n')
        line_count = len(lines)
        text_widget.config(height=max(line_count, 2))

    def populate_fields(self):
        if self.values:
            for i, key in enumerate(self.entries.keys()):
                widget = self.entries[key]
                if isinstance(widget, tk.Entry):
                    widget.insert(0, self.values[i + 1])
                elif isinstance(widget, tk.Text):
                    widget.insert("1.0", self.values[i + 1])

    def validate_entries(self):
        for label, entry in self.entries.items():
            if isinstance(entry, tk.Entry):
                if not entry.get():
                    messagebox.showerror("Validation Error", f"{label} is required.")
                    return False
            elif isinstance(entry, tk.Text):
                if not entry.get("1.0", "end-1c").strip():
                    messagebox.showerror("Validation Error", f"{label} is required.")
                    return False
        return True

    def save_task(self):
        if not self.validate_entries():
            return

        data = []
        for entry in self.entries.values():
            if isinstance(entry, tk.Entry):
                data.append(entry.get())
            elif isinstance(entry, tk.Text):
                data.append(entry.get("1.0", "end-1c").strip())

        if self.values:
            data.append(self.values[-1])
            self.db.update_data(data)
        else:
            self.db.insert_data(data)

        self.task_manager.load_data()
        self.destroy()

    def style_buttons(self):
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10), padding=5)
