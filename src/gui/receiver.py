import tkinter as tk
from gui.change_page import change_page

class Receiver(tk.Frame):
    def __init__(self, container, handler):
        super().__init__(container, bg='#D9D9D9')

        self.handler = handler
        self.next_page = None
        
        frame1 = tk.Frame(self)
        embed_button = tk.Button(frame1, text= 'EMBED', fg='white', bg='#35915B',
                                  width=13, font=("Arial", 10, "bold"), relief=tk.FLAT,
                                   command=lambda: self.handler.change_page(self, self.next_page))
        extract_button = tk.Button(frame1, text= 'EXTRACT', fg='white', bg='#D58B1B',
                                   width=13, font=("Arial", 10, "bold"), relief=tk.FLAT) 

        label3 = tk.Label(self, text= 'Receiver', background='red')

        frame1.pack(fill='both', pady= 10)
        embed_button.pack(side='left', ipady=6, ipadx= 7, padx= 10)
        extract_button.pack(side='left', ipady=6, ipadx= 7)

        label3.pack(fill='both', expand=True)
    
    def set_next_page(self, page):
        self.next_page = page