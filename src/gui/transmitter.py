import tkinter as tk
from tkinter import ttk
from gui.change_page import change_page

class Transmitter(tk.Frame):
    def __init__(self, container, handler):
        super().__init__(container)

        self.handler = handler
        self.next_page = None
        
        frame1 = ttk.Frame(self)
        embed_button = tk.Button(frame1, text= 'EMBED_button', fg='white', bg='#35915B')
        extract_button = tk.Button(frame1, text= 'EXTRACT', fg='white', bg='#D58B1B', 
                                   command=lambda: self.handler.change_page(self, self.next_page))

        label3 = ttk.Label(self, text= 'Transmitter', background='blue')

        frame1.pack(fill='both', pady= 5)
        embed_button.pack(side='left', ipady=6, ipadx= 7)
        extract_button.pack(side='left', ipady=6, ipadx= 7)

        label3.pack(fill='both', expand=True)
    
    def set_next_page(self, page):
        self.next_page = page