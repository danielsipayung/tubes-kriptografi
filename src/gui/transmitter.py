import tkinter as tk
from gui.change_page import change_page
from utils.file_handler import File_handler

from steganography.avi_process import extract_frames, rebuild_video
from steganography.text_file_binary import text_to_binary, binary_to_text, file_to_binary, binary_to_file
from steganography.steganography import split_byte_332, generate_header, get_frame_order, embed_secret, extract_secret, default_delimiter

from tkvideo import tkvideo
import os

class Transmitter(tk.Frame):
    def __init__(self, container, handler):
        super().__init__(container, bg='#D9D9D9')

        self.handler = handler
        self.next_page = None

        self.path = File_handler()
        self.path2 = ''
        
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
        frame3a = tk.Frame(frame3, bg="#53B27B")
        label3a = tk.Label(frame3a, text= 'Cover Video', font=("Arial", 16, "bold"), bg='#35915B', fg='white')
        label3a.pack(fill='both')
        self.label3a1 = tk.Label(frame3a, text= 'Video', font=("Arial", 16, "bold"), bg="#000000", pady=6)
        self.label3a1.pack(fill='both')
        button3a = tk.Button(frame3a, text= 'Select file', font=("Arial", 10, "bold"), fg='white', 
                             bg="#982011", pady=3, relief=tk.FLAT, command=self.pick_file)
        button3a.pack(ipadx= 10, pady= 5)

        #   # 3b
        self.frame3b = tk.Frame(frame3, bg="#53B27B")
        label3b = tk.Label(self.frame3b, text= 'Secret Message', font=("Arial", 16, "bold"), bg='#35915B', fg='white')
        label3b.pack(fill='both')
        self.label3b1 = tk.Label(self.frame3b, text= ' ', font=("Arial", 12, "bold"), bg="#000000", fg='white', pady=6)
        self.label3b1.pack(fill='both',ipady=39)
        button3b = tk.Button(self.frame3b, text= 'Select file', font=("Arial", 10, "bold"), fg='white', 
                             bg='#982011', pady=3, relief=tk.FLAT, command=self.pick_file2)
        button3b.pack(ipadx= 10, pady= 5)

        #   # 3c
        frame3c = tk.Frame(frame3, bg="#B9BB11")
        label3c = tk.Label(frame3c, text= 'Stego Video', font=("Arial", 16, "bold"), bg="#B9BB11", fg='white')
        label3c.pack(fill='both')
        label3c1 = tk.Label(frame3c, text= 'Video', font=("Arial", 16, "bold"), bg="#000000", pady=6)
        label3c1.pack(fill='both', ipady=40)
        button3c = tk.Button(frame3c, text= 'save', font=("Arial", 10, "bold"), fg='white', 
                             bg='#111111', pady=3, relief=tk.FLAT, command=self.path.save_file,
                             highlightbackground="white")
        button3c.pack(ipadx= 10, pady= 5)

        frame3.pack(fill='both', ipady= 0)
        frame3a.pack(side='left',fill='both', expand=True)
        self.frame3b.pack(side='left',fill='both', expand=True)
        frame3c.pack(side='left',fill='both', expand=True)
    
        # FRAME 4

        self.use_encryption = tk.BooleanVar(value=False)

        frame4 = tk.Frame(self, bg='#D9D9D9')
        check_button = tk.Checkbutton(frame4,bg='#D9D9D9',
                                      variable=self.use_encryption,
                                      command= self.toggle_entry)
        label4 = tk.Label(frame4, text= 'Use encryption', font=("Arial", 12), justify='left', bg='#D9D9D9')

        frame4.pack(fill='both', pady= 10, padx=(17,0))
        label4.pack(anchor='w', side='left')
        check_button.pack(side='left')

        # FRAME 5
        frame5 = tk.Frame(self, bg='#D9D9D9')
        label5 = tk.Label(frame5, text= 'A5/1 key', font=("Arial", 12), justify='left', bg='#D9D9D9')
        self.entry5 = tk.Entry(frame5, bg='black', font=("Arial", 12), state='disabled', disabledbackground="#000000")

        frame5.pack(fill='both', padx=(17,0))
        label5.pack(anchor='w', side='top')
        self.entry5.pack(side = 'top', anchor='w', expand=True, fill='x', ipady= 5, padx=(0,17))

        # FRAME 6

        frame6 = tk.Frame(self, bg='#D9D9D9')
        label6 = tk.Label(frame6, text= 'Insertion method', font=("Arial", 12), justify='left', bg='#D9D9D9')
        
        self.var2 = tk.StringVar(value="sequential")
        self.var2.trace_add("write", self.stego_choice)

        options = ["sequential", "random"]
        dropdown = tk.OptionMenu(frame6, self.var2, *options)

        frame6.pack(fill='both', pady= 14, padx=(17,0))
        label6.pack(anchor='w', side='left')
        dropdown.config(bg='#ACACAC', width=15, relief='flat', highlightbackground="black")
        dropdown.pack(side='left', padx=10, pady=5)

        # FRAME 7

        frame7 = tk.Frame(self, bg='#D9D9D9')
        label7 = tk.Label(frame7, text= 'Stego key', font=("Arial", 12), justify='left', bg='#D9D9D9', fg='black')
        self.entry7 = tk.Entry(frame7, font=("Arial", 12), state='disabled', disabledbackground="#000000")

        frame7.pack(fill='both', pady= 0, padx=(17,0))
        label7.pack(anchor='w', side='top')
        self.entry7.pack(side = 'top', anchor='w', expand=True, fill='x', ipady= 5, padx=(0,17))

        # FRAME 8
        frame8 = tk.Frame(self, bg='#D9D9D9')
        Embed_message_button = tk.Button(self, text='Embed Message', font=("Arial", 12, "bold"), 
                                         bg='#947A1D', fg='white', relief=tk.FLAT)

        frame8.pack(fill='both', pady= 10)
        Embed_message_button.pack(side='top', ipady=6, ipadx= 80, padx= 10)


    def set_next_page(self, page):
        self.next_page = page

    def toggle_entry(self):
        if self.use_encryption.get():
            self.entry5.config(state='normal', bg="#FFFFFF")
        else:
            self.entry5.delete(0, tk.END)
            self.entry5.config(state='disabled')

    def stego_choice(self, *args):
        if self.var2.get() == "random":
            self.entry7.config(state='normal', bg='#FFFFFF') 
        else:
            self.entry7.delete(0, tk.END)
            self.entry7.config(state='disabled', bg='#808080')
    
    def pick_file(self):
        file_name = self.path.open_file()
        extract_frames(file_name, "Gyokeres")
        if file_name:
            self.video_path = file_name
            self.start_video_preview(file_name)
        pass

    def pick_file2(self):
        message = os.path.basename(self.path.open_file())
        self.label3b1.config(text=f"Message: {message}")
        pass

    def embed(self):


        pass

    def start_video_preview(self,path):
        self.player = tkvideo(path, self.label3a1, loop=1, size=(192,108))

        self.player.play()
        pass

