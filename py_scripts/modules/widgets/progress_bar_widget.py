from tkinter import Frame, ttk

class ProgressBarWidget(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=300)
        self.progress_bar.pack(pady=10)

    def update_progress(self, value):
        self.progress_bar["value"] = value
        self.update_idletasks()
