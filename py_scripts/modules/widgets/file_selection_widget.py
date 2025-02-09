from tkinter import Frame, Label, Entry, Button, filedialog

class FileSelectionWidget(Frame):
    def __init__(self, parent, label_text, var):
        super().__init__(parent)
        self.var = var
        Label(self, text=label_text).pack(side="left")
        Entry(self, textvariable=self.var, width=40).pack(side="left")
        Button(self, text="Browse", command=self.browse_file).pack(side="left")

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.var.set(file_path)
