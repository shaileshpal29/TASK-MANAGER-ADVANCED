# ui_components.py

import tkinter as tk
from tkinter import ttk

def create_label(parent, text, row, column, font=("Helvetica", 14), bg='lightgrey', sticky='w', padx=10, pady=5):
    label = tk.Label(parent, text=text, font=font, bg=bg)
    label.grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)
    return label

def create_entry(parent, row, column, font=("Helvetica", 12), bd=2, sticky='ew', ipadx=10, ipady=5, padx=10, pady=5):
    entry = tk.Entry(parent, font=font, bd=bd)
    entry.grid(row=row, column=column, sticky=sticky, ipadx=ipadx, ipady=ipady, padx=padx, pady=padx)
    return entry

def create_text(parent, row, column, height=2, width=40, wrap='word', font=("Helvetica", 12), bd=2, sticky='ew', ipadx=10, ipady=5, padx=10, pady=5):
    text = tk.Text(parent, height=height, width=width, wrap=wrap, font=font, bd=bd)
    text.grid(row=row, column=column, sticky=sticky, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady)
    return text

def create_combobox(parent, row, column, values, font=("Helvetica", 12), sticky='ew', ipadx=10, ipady=5, padx=10, pady=5):
    combobox = ttk.Combobox(parent, font=font, values=values)
    combobox.grid(row=row, column=column, sticky=sticky, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady)
    return combobox

def create_button(parent, text, command, row, column, font=("Helvetica", 10), padding=5, padx=5, pady=5, columnspan=1):
    button = ttk.Button(parent, text=text, command=command)
    button.grid(row=row, column=column, padx=padx, pady=pady, columnspan=columnspan)
    return button

def create_frame(parent, row, column, sticky='ew', padx=5, pady=5, columnspan=1):
    frame = ttk.Frame(parent)
    frame.grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady, columnspan=columnspan)
    return frame
