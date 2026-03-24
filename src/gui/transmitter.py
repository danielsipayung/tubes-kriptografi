import tkinter as tk

class Transmitter(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        label = tk.Label(self, text="Transmitter")
        label.pack(pady=50)