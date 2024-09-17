# advanced_features.py

from tkinter import simpledialog, messagebox

def analyze_tasks(db):
    data = db.fetch_data()
    total_tasks = len(data)
    status_count = {
        'Done': 0,
        'Pending': 0,
        'Descoped': 0,
        'Blocker': 0,
        'Inprogress': 0,
        'Closed': 0
    }

    for row in data:
        status_count[row[3]] += 1

    analysis_text = f"Total Tasks: {total_tasks}\n"
    for status, count in status_count.items():
        analysis_text += f"{status}: {count}\n"

    messagebox.showinfo("Data Analysis", analysis_text)

def search_tasks(db, tree):
    search_term = simpledialog.askstring("Search Tasks", "Enter task keyword or status to search:")
    if search_term:
        for item in tree.get_children():
            tree.delete(item)

        data = db.fetch_data()
        search_results = [row for row in data if search_term.lower() in row[2].lower() or search_term.lower() in row[3].lower()]

        for seq_no, row in enumerate(search_results, start=1):
            tree.insert('', 'end', values=(seq_no, *row[1:], row[0]))
