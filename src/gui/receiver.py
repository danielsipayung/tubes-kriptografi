import tkinter as tk

class Receiver(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        label = tk.Label(self, text="Receiver")
        label.pack(pady=50)