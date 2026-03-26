import tkinter as tk
from gui.change_page import change_page
from utils.file_handler import File_handler

class Transmitter(tk.Frame):
    def __init__(self, container, handler):
        super().__init__(container, bg='#D9D9D9')

        self.handler = handler
        self.next_page = None

        path = File_handler()
        
        # FRAME 1
        frame1 = tk.Frame(self, bg='#D9D9D9')
        embed_button = tk.Button(frame1, text= 'EMBED', fg='white', bg='#35915B', 
                                    width=13, font=("Arial", 10, "bold"), relief=tk.FLAT)
        extract_button = tk.Button(frame1, text= 'EXTRACT', fg='white', bg='#D58B1B',
                                    width=13, font=("Arial", 10, "bold"), relief=tk.FLAT,
                                   command=lambda: self.handler.change_page(self, self.next_page))

        frame1.pack(fill='both', pady= 10)
        embed_button.pack(side='left', ipady=6, ipadx= 7, padx= 10)
        extract_button.pack(side='left', ipady=6, ipadx= 7)

        # FRAME 2
        frame2 = tk.Frame(self, bg='#D9D9D9')
        label2 = tk.Label(frame2, text= 'Transmitter', font=("Arial", 20, "bold"), bg='#D9D9D9')

        label2.pack(anchor='w',side='top')
        frame2.pack(fill='both', pady= 8, padx=(10,0))

        # FRAME 3
        frame3 = tk.Frame(self, bg="#FFFFFF")

        #   # 3a
        frame3a = tk.Frame(frame3, bg="#FF0808")
        label3a = tk.Label(frame3a, text= 'Cover Video', font=("Arial", 16, "bold"), bg='#FF0808', fg='white')
        label3a.pack(fill='both')
        label3a1 = tk.Label(frame3a, text= 'Video', font=("Arial", 16, "bold"), bg="#000000", pady=6)
        label3a1.pack(fill='both', ipady=40)
        button3a = tk.Button(frame3a, text= 'Select file', font=("Arial", 10, "bold"), fg='white', 
                             bg='#006989', pady=3, relief=tk.FLAT, command=path.open_file)
        button3a.pack(ipadx= 10, pady= 5)

        #   # 3b
        frame3b = tk.Frame(frame3, bg="#0008FF")
        label3b = tk.Label(frame3b, text= 'Secret Message', font=("Arial", 16, "bold"), bg='#0008FF', fg='white')
        label3b.pack(fill='both')
        label3b1 = tk.Label(frame3b, text= 'Video', font=("Arial", 16, "bold"), bg="#000000", pady=6)
        label3b1.pack(fill='both', ipady=40)
        button3b = tk.Button(frame3b, text= 'Select file', font=("Arial", 10, "bold"), fg='white', 
                             bg='#006989', pady=3, relief=tk.FLAT, command=path.open_file)
        button3b.pack(ipadx= 10, pady= 5)

        #   # 3c
        frame3c = tk.Frame(frame3, bg="#B9BB11")
        label3c = tk.Label(frame3c, text= 'Stego Video', font=("Arial", 16, "bold"), bg="#B9BB11", fg='white')
        label3c.pack(fill='both')
        label3c1 = tk.Label(frame3c, text= 'Video', font=("Arial", 16, "bold"), bg="#000000", pady=6)
        label3c1.pack(fill='both', ipady=40)
        button3c = tk.Button(frame3c, text= 'save', font=("Arial", 10, "bold"), fg='white', 
                             bg='#111111', pady=3, relief=tk.FLAT, command=path.save_file)
        button3c.pack(ipadx= 10, pady= 5)

        frame3.pack(fill='both', ipady= 0)
        frame3a.pack(side='left',fill='both', expand=True)
        frame3b.pack(side='left',fill='both', expand=True)
        frame3c.pack(side='left',fill='both', expand=True)
    
        # FRAME 4
        frame4 = tk.Frame(self, bg='#D9D9D9')
        label4 = tk.Label(frame4, text= 'Use encryption', font=("Arial", 12), justify='left', bg='#D9D9D9')
        label4a = tk.Label(frame4, text= 'yes', font=("Arial", 12, "bold"), justify='left', bg='#D9D9D9')

        frame4.pack(fill='both', pady= 10, padx=(17,0))
        label4.pack(anchor='w', side='left')
        label4a.pack(anchor='w', side='left')

        # FRAME 5
        frame5 = tk.Frame(self, bg='#D9D9D9')
        label5 = tk.Label(frame5, text= 'A5/1 key', font=("Arial", 12), justify='left', bg='#D9D9D9')
        label5a = tk.Label(frame5, text= ' ', font=("Arial", 12), justify='left', bg='#ACACAC')

        frame5.pack(fill='both', pady= 0, padx=(17,0))
        label5.pack(anchor='w', side='top')
        label5a.pack(anchor='w', side='top', expand=True, fill='x', ipady= 5, padx=(0,17))

        # FRAME 6
        frame6 = tk.Frame(self, bg='#D9D9D9')
        label6 = tk.Label(frame6, text= 'Insertion method', font=("Arial", 12), justify='left', bg='#D9D9D9')
        label6a = tk.Label(frame6, text= 'sequential', font=("Arial", 12, "bold" ), justify='left', bg='#D9D9D9')

        frame6.pack(fill='both', pady= 14, padx=(17,0))
        label6.pack(anchor='w', side='left')
        label6a.pack(anchor='w', side='left')

        # FRAME 7
        frame7 = tk.Frame(self, bg='#D9D9D9')
        label7 = tk.Label(frame7, text= 'Stego key', font=("Arial", 12), justify='left', bg='#D9D9D9')
        label7a = tk.Label(frame7, text= ' ', font=("Arial", 12), justify='left', bg='#ACACAC')

        frame7.pack(fill='both', pady= 0, padx=(17,0))
        label7.pack(anchor='w', side='top')
        label7a.pack(anchor='w', side='top', expand=True, fill='x', ipady= 5, padx=(0,17))

        # FRAME 8
        frame8 = tk.Frame(self, bg='#D9D9D9')
        Embed_message_button = tk.Button(self, text='Embed Message', font=("Arial", 12, "bold"), 
                                         bg='#947A1D', fg='white', relief=tk.FLAT)

        frame8.pack(fill='both', pady= 10)
        Embed_message_button.pack(side='top', ipady=6, ipadx= 80, padx= 10)


    def set_next_page(self, page):
        self.next_page = page