from modules.rbUI import rbUI
from modules.rbEvents import rbEvents
from tkinter import messagebox
import os

import tkinter as tk
import modules.fileUtility as f


class LightingMacroImportTool:
    def __init__(self, root):
        self.ui = rbUI(root)
        self.events = rbEvents(self.ui)
        self.ui.events = self.events

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if os.path.exists(app.ui.temp_dir):
            f.clearTempFolder(app.ui.temp_dir)
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LightingMacroImportTool(root)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.createcommand('tk::mac::Quit', on_closing)

    root.mainloop()
