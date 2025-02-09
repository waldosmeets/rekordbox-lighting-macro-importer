import sqlite3
import glob
import os
import json
import tkinter as tk

from tkinter import messagebox
from modules.constants import CONFIG_FILE

def log_status(status_logger, message):
    """Log a message to the status text box."""
    if status_logger:
        status_logger.config(state="normal")
        status_logger.insert("end", f"{message}\n")
        status_logger.see("end")
        status_logger.config(state="disabled")


# Additional utility function to disable widgets in a frame
def disable_widgets_in_frame(frame):
    """Disable all entry and button widgets in a given frame."""
    for widget in frame.winfo_children():
        if isinstance(widget, (tk.Entry, tk.Button)):
            widget.config(state="disabled")

# Additional utility function to enable widgets in a frame
def enable_widgets_in_frame(frame):
    """Enable all entry and button widgets in a given frame."""
    for widget in frame.winfo_children():
        if isinstance(widget, (tk.Entry, tk.Button)):
            widget.config(state="normal")
