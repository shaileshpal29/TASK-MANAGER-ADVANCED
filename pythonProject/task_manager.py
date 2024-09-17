# task_manager.py

import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
import csv
from database import Database
from task_form import TaskForm
from playsound import playsound
import threading
from ui_components import create_button, create_frame
from advanced_features import analyze_tasks, search_tasks

class TaskManager:
    def __init__(self, parent, db_name):
        self.parent = parent
        self.db = Database(db_name)
        self.setup_ui()
        self.log_text = self.create_log_text()
        self.db.notify_change = self.load_data
        self.refresh_interval = 30000
        self.start_auto_refresh()

    def setup_ui(self):
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.tree = self.create_treeview()
        self.create_scrollbars()
        self.create_buttons()
        self.load_data()
        self.setup_event_bindings()

    def create_treeview(self):
        columns = [
            'Seq No', 'Assigned Date', 'Task', 'Status', 'Completion Date', 'Issue',
            'Remark', 'Test Result Path', 'Assigned To', 'Priority', 'Progress percentage', 'ID'
        ]
        tree = ttk.Treeview(self.parent, columns=columns, show='headings')
        for col in columns[:-1]:
            tree.heading(col, text=col, command=lambda _col=col: self.sort_column(_col, False))
            tree.column(col, width=150)
        tree.column('ID', width=0, stretch=tk.NO)
        tree.grid(row=0, column=0, sticky='nsew')
        self.bind_column_resize(tree)
        tree.bind('<Double-1>', self.on_double_click)
        tree.bind('<Control-c>', self.copy_selected_row)  # Bind Ctrl+C to the treeview
        return tree

    def on_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            TaskForm(self.parent, self, self.db, item['values'], selected_item)

    def copy_selected_row(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            values = item['values']
            self.parent.clipboard_clear()
            self.parent.clipboard_append(','.join(str(v) for v in values))
            messagebox.showinfo("Copy", "Selected row copied to clipboard")




    def bind_column_resize(self, tree):
        def handle_column_resize(event):
            tree.update_idletasks()
            self.parent.grid_columnconfigure(0, weight=1)

        for col in tree['columns']:
            tree.heading(col, text=col, command=lambda _col=col: self.sort_column(_col, False))
            tree.column(col, width=150, minwidth=50, stretch=True)

        tree.bind('<Configure>', handle_column_resize)
        tree.bind('<ButtonRelease-1>', handle_column_resize)
        tree.bind('<<TreeviewColumnMoved>>', handle_column_resize)

    def create_scrollbars(self):
        vsb = ttk.Scrollbar(self.parent, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        hsb = ttk.Scrollbar(self.parent, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky='ew')
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.parent.grid_rowconfigure(1, weight=0)
        self.parent.grid_columnconfigure(1, weight=0)

        def adjust_scroll_region(event):
            self.tree.update_idletasks()

        self.tree.bind('<Configure>', adjust_scroll_region)
        self.tree.bind('<ButtonRelease-1>', adjust_scroll_region)
        self.tree.bind('<<TreeviewColumnMoved>>', adjust_scroll_region)

    def create_buttons(self):
        button_frame = create_frame(self.parent, 2, 0, columnspan=2)

        buttons = [
            ("Add", self.add_task),
            ("Edit", self.edit_task),
            ("Delete", self.delete_task),
            ("Filter", self.filter_tasks),
            ("Reset Filter", self.reset_filter),
            ("Download", self.download_data),
            ("Import", self.import_data),
            ("Reminder", self.set_reminder),
            ("Analyze", self.analyze_data),
            ("Search", self.search_tasks)
        ]

        for i, (text, command) in enumerate(buttons):
            create_button(button_frame, text, command, 0, i, columnspan=1)

    def load_data(self, filter_status=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        data = self.db.fetch_data()
        visible_data = [row for row in data if row[3] != 'Closed'] if filter_status is None else data

        for seq_no, row in enumerate(visible_data, start=1):
            if filter_status and row[3] != filter_status:
                continue
            self.tree.insert('', 'end', values=(seq_no, *row[1:], row[0]))

        self.color_rows()

    def color_rows(self):
        for item in self.tree.get_children():
            status = self.tree.item(item, 'values')[3]
            tags = {
                'Done': 'done',
                'Pending': 'pending',
                'Descoped': 'descoped',
                'Blocker': 'blocker',
                'Inprogress': 'inprogress',
                'Closed': 'closed'
            }.get(status, '')

            self.tree.item(item, tags=tags)

        style = ttk.Style()
        style.configure("Treeview", rowheight=35)

        self.tree.tag_configure('done', background='#d4edda')
        self.tree.tag_configure('pending', background='#d1ecf1')
        self.tree.tag_configure('descoped', background='#fff3cd')
        self.tree.tag_configure('blocker', background='#f8d7da')
        self.tree.tag_configure('inprogress', background='#fff3e0')
        self.tree.tag_configure('closed', background='#f5f5f5')

    def add_task(self):
        TaskForm(self.parent, self, self.db)

    def edit_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            TaskForm(self.parent, self, self.db, item['values'], selected_item)

    def delete_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            try:
                self.db.delete_data(item['values'][-1])
                self.load_data()
            except Exception as e:
                self.log_error(f"Delete error: {e}")

    def filter_tasks(self):
        search_term = simpledialog.askstring(
            "Input",
            "Enter status to filter by (e.g., 'Done', 'Pending', 'Descoped', 'Blocker', 'Inprogress', 'Closed'):"
        )
        if search_term:
            search_term = search_term.lower()
            self.load_data(filter_status=search_term.capitalize())
            self.color_rows()

    def reset_filter(self):
        self.load_data()

    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda _col=col: self.sort_column(_col, not reverse))
        self.color_rows()

    '''def download_data(self):
        columns_to_export = simpledialog.askstring("Select Columns", "Enter columns to export (comma-separated):")
        if columns_to_export:
            columns = [col.strip() for col in columns_to_export.split(',')]
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(columns)
                    data = self.db.fetch_data()
                    for row in data:
                        writer.writerow([row[self.tree['columns'].index(col)] for col in columns])'''

    def download_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'Seq No', 'Assigned Date', 'Task', 'Status', 'Completion Date', 'Issue',
                    'Remark', 'Test Result Path', 'Assigned To', 'Priority', 'Progress percentage'
                ])
                data = self.db.fetch_data()
                for seq_no, row in enumerate(data, start=1):
                    writer.writerow([seq_no, *row[1:]])

    def import_data(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)
                    for row in reader:
                        self.db.insert_data(row[1:])
                self.load_data()
            except Exception as e:
                self.log_error(f"Import error: {e}")

    def set_reminder(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            time = simpledialog.askstring("Reminder",
                                          "Enter reminder time in the format 'H:M' (hours:minutes), 'M' (minutes) or 'D' (days):")
            if time:
                try:
                    total_seconds = self.parse_time(time)
                    task_details = item['values'][2]
                    threading.Timer(total_seconds, self.reminder_notification, args=[task_details]).start()
                except ValueError:
                    messagebox.showerror("Error", "Invalid time format. Please enter in 'H:M', 'M', or 'D' format.")

    def parse_time(self, time):
        if ':' in time:
            hours, minutes = map(int, time.split(':'))
            total_seconds = hours * 3600 + minutes * 60
        elif 'm' in time.lower():
            minutes = int(time.lower().replace('m', '').strip())
            total_seconds = minutes * 60
        else:
            days = int(time)
            total_seconds = days * 86400
        return total_seconds

    def reminder_notification(self, task):
        playsound(r"C:\Task_Manager_12\pythonProject\notification_sound.mp3")
        messagebox.showinfo("Reminder", f"Reminder for task: {task}")

    def analyze_data(self):
        analyze_tasks(self.db)

    def search_tasks(self, event=None):
        search_term = simpledialog.askstring("Search Tasks", "Enter task keyword or status to search:")
        if search_term:
            for item in self.tree.get_children():
                self.tree.delete(item)

            data = self.db.fetch_data()
            search_results = [row for row in data if
                              search_term.lower() in row[2].lower() or search_term.lower() in row[3].lower()]

            for seq_no, row in enumerate(search_results, start=1):
                self.tree.insert('', 'end', values=(seq_no, *row[1:], row[0]))

    def setup_event_bindings(self):
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Control-c>', self.copy_selected_row)
        self.parent.bind_all('<Control-f>', self.search_tasks)

    def log_error(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def create_log_text(self):
        log_text = tk.Text(self.parent, height=3, bg="#f5f5f5", fg="red", state='normal')
        log_text.grid(row=3, column=0, columnspan=2, sticky='ew')
        log_text.config(state='normal')
        return log_text

    def start_auto_refresh(self):
        self.load_data()
        self.parent.after(self.refresh_interval, self.start_auto_refresh)

    def setup_event_bindings(self):
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Control-c>', self.copy_selected_row)
        self.parent.bind_all('<Control-f>', self.search_tasks)
