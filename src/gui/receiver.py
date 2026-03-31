import tkinter as tk
from tkinter import messagebox, filedialog
import os, threading

from gui.change_page import change_page
from utils.file_handler import File_handler
from steganography.avi_process import AviProcess, BASE_DIR
from steganography.text_file_binary import BinaryConverter
from steganography.steganography import Steganography
from crypto.a51 import A51
from tkvideo import tkvideo

FRAMES_FOLDER = "ReceiverFrames"


class Receiver(tk.Frame):
    def __init__(self, container, handler):
        super().__init__(container, bg='#D9D9D9')

        self.handler = handler
        self.next_page = None
        self.path  = File_handler()
        self.avi   = AviProcess()
        self.conv  = BinaryConverter()
        self.stega = Steganography()

        self.stego_path = None
        self.extracted_data = None
        self.extracted_ext = ""
        self.extracted_fname = ""

        frame1 = tk.Frame(self, bg='#D9D9D9')
        embed_button = tk.Button(frame1, text='EMBED', fg='white', bg='#35915B',
                                 width=13, font=("Arial", 10, "bold"), relief=tk.FLAT,
                                 command=lambda: self.handler.change_page(self, self.next_page))
        extract_button = tk.Button(frame1, text='EXTRACT', fg='white', bg='#D58B1B',
                                   width=13, font=("Arial", 10, "bold"), relief=tk.FLAT)
        frame1.pack(fill='both', pady=10)
        embed_button.pack(side='left', ipady=6, ipadx=7, padx=10)
        extract_button.pack(side='left', ipady=6, ipadx=7)

        frame2 = tk.Frame(self, bg='#D9D9D9')
        tk.Label(frame2, text='Receiver', font=("Arial", 20, "bold"), bg='#D9D9D9').pack(anchor='w')
        frame2.pack(fill='both', pady=8, padx=(10, 0))

        frame3 = tk.Frame(self, bg="#FFFFFF")

        frame3a = tk.Frame(frame3, bg="#53B27B")
        tk.Label(frame3a, text='Stego Video', font=("Arial", 16, "bold"), bg='#35915B', fg='white').pack(fill='both')
        self.label3a1 = tk.Label(frame3a, text='Video', font=("Arial", 16, "bold"), bg="#000000", pady=6)
        self.label3a1.pack(fill='both', ipady=0)
        tk.Button(frame3a, text='Select file', font=("Arial", 10, "bold"), fg='white',
                  bg="#982011", pady=3, relief=tk.FLAT,
                  command=self.pick_stego_file).pack(ipadx=10, pady=5)

        self.frame3b = tk.Frame(frame3, bg="#53B27B")
        tk.Label(self.frame3b, text='Secret Message', font=("Arial", 16, "bold"), bg='#35915B', fg='white').pack(fill='both')
        self.label3b1 = tk.Label(self.frame3b, text=' ', font=("Arial", 12, "bold"), bg="#000000", fg='white', pady=6)
        self.label3b1.pack(fill='both', ipady=39)
        self.button3b = tk.Button(self.frame3b, text='Save', font=("Arial", 10, "bold"), fg='white',
                                  bg='#111111', pady=3, relief=tk.FLAT, command=self.save_message,
                                  highlightbackground="white", state='disabled')
        self.button3b.pack(ipadx=10, pady=5)

        frame3.pack(fill='both')
        frame3a.pack(side='left', fill='both', expand=True)
        self.frame3b.pack(side='left', fill='both', expand=True)

        self.use_encryption = tk.BooleanVar(value=False)
        frame4 = tk.Frame(self, bg='#D9D9D9')
        tk.Label(frame4, text='Use encryption', font=("Arial", 12), bg='#D9D9D9').pack(anchor='w', side='left')
        tk.Checkbutton(frame4, bg='#D9D9D9', variable=self.use_encryption,
                       command=self.toggle_entry).pack(side='left')
        frame4.pack(fill='both', pady=10, padx=(17, 0))

        frame5 = tk.Frame(self, bg='#D9D9D9')
        tk.Label(frame5, text='A5/1 key', font=("Arial", 12), bg='#D9D9D9').pack(anchor='w')
        self.entry5 = tk.Entry(frame5, bg='black', font=("Arial", 12), state='disabled', disabledbackground="#000000")
        self.entry5.pack(anchor='w', expand=True, fill='x', ipady=5, padx=(0, 17))
        frame5.pack(fill='both', padx=(17, 0))

        self.var2 = tk.StringVar(value="sequential")
        self.var2.trace_add("write", self.stego_choice)
        frame6 = tk.Frame(self, bg='#D9D9D9')
        tk.Label(frame6, text='Insertion method', font=("Arial", 12), bg='#D9D9D9').pack(anchor='w', side='left')
        dropdown = tk.OptionMenu(frame6, self.var2, "sequential", "random")
        dropdown.config(bg='#ACACAC', width=15, relief='flat', highlightbackground="black")
        dropdown.pack(side='left', padx=10, pady=5)
        frame6.pack(fill='both', pady=14, padx=(17, 0))

        frame7 = tk.Frame(self, bg='#D9D9D9')
        tk.Label(frame7, text='Stego key', font=("Arial", 12), bg='#D9D9D9').pack(anchor='w')
        self.entry7 = tk.Entry(frame7, font=("Arial", 12), state='disabled', disabledbackground="#000000")
        self.entry7.pack(anchor='w', expand=True, fill='x', ipady=5, padx=(0, 17))
        frame7.pack(fill='both', padx=(17, 0))

        tk.Frame(self, bg='#D9D9D9').pack(fill='both', pady=10)
        tk.Button(self, text='Extract Message', font=("Arial", 12, "bold"),
                  bg='#947A1D', fg='white', relief=tk.FLAT,
                  command=self.extract).pack(ipady=6, ipadx=80, padx=10)

    def set_next_page(self, page):
        self.next_page = page

    def toggle_entry(self):
        if self.use_encryption.get():
            self.entry5.config(state='normal', bg="#FFFFFF")
        else:
            self.entry5.delete(0, tk.END)
            self.entry5.config(state='disabled')

    def stego_choice(self, *_):
        if self.var2.get() == "random":
            self.entry7.config(state='normal', bg='#FFFFFF')
        else:
            self.entry7.delete(0, tk.END)
            self.entry7.config(state='disabled', bg='#808080')

    def pick_stego_file(self):
        file_name = self.path.open_file()
        if not file_name:
            return
        self.stego_path = file_name
        self.label3a1.config(text="Mengekstrak frame...", bg='#333333', fg='white')

        def _run():
            try:
                self.avi.extract_frames(file_name, FRAMES_FOLDER)
                self.after(0, lambda: self.start_video_preview(file_name))
            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Error", str(err)))

        threading.Thread(target=_run, daemon=True).start()

    def start_video_preview(self, path):
        self.player = tkvideo(path, self.label3a1, loop=1, size=(192, 108))
        self.player.play()

    def extract(self):
        if not self.stego_path:
            messagebox.showerror("Error", "Pilih stego video terlebih dahulu.")
            return

        mode = self.var2.get()
        stego_key = self.entry7.get().strip() if mode == "random" else None

        if mode == "random" and not stego_key:
            messagebox.showerror("Error", "Masukkan stego key untuk mode random.")
            return

        frames_path = os.path.join(BASE_DIR, "avi_frames", FRAMES_FOLDER)
        if not os.path.exists(frames_path):
            messagebox.showerror("Error", "Frame folder tidak ditemukan. Pilih ulang stego video.")
            return

        frame_order = self.stega.get_sorted_frame_order(frames_path)
        if not frame_order:
            messagebox.showerror("Error", "Tidak ada frame yang ditemukan.")
            return

        use_enc = self.use_encryption.get()
        a51_key = self.entry5.get().strip() if use_enc else None

        self.button3b.config(state='disabled')
        self.label3b1.config(text="Mengekstrak pesan...", fg='yellow')

        def _run():
            try:
                header, binary_bits = self.stega.extract_secret(
                    frames_path, frame_order, mode=mode, stego_key=stego_key
                )
            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Error", str(err)))
                return

            if header is None:
                self.after(0, lambda: messagebox.showerror(
                    "Error", "Header tidak ditemukan. Pesan mungkin tidak tersimpan dengan benar."))
                return

            if use_enc or header.get("encrypted", False):
                if not a51_key:
                    self.after(0, lambda: messagebox.showerror("Error", "Masukkan A5/1 key untuk dekripsi."))
                    return
                try:
                    cipher = A51(a51_key)
                    decrypted = cipher.enc_block([int(b) for b in binary_bits])
                    binary_bits = ''.join(map(str, decrypted))
                except ValueError as e:
                    self.after(0, lambda err=e: messagebox.showerror("Error", f"Dekripsi gagal: {err}"))
                    return

            data = bytes([int(binary_bits[i:i+8], 2) for i in range(0, len(binary_bits), 8)])
            self.after(0, lambda h=header, d=data: self._finish_extract(h, d))

        threading.Thread(target=_run, daemon=True).start()

    def _finish_extract(self, header, data):
        self.extracted_data  = data
        self.extracted_ext   = header.get("extension", "")
        self.extracted_fname = header.get("filename", "output" + self.extracted_ext)

        if header["file_type"] == "text":
            try:
                text_preview = data.decode("utf-8")
            except UnicodeDecodeError:
                text_preview = data.decode("utf-8", errors="replace")
            display = text_preview[:40] + ("..." if len(text_preview) > 40 else "")
            self.label3b1.config(text=f"Teks: {display}", wraplength=180, fg='white')
        else:
            size_kb = len(data) / 1024
            self.label3b1.config(text=f"File: {self.extracted_fname}\n{size_kb:.1f} KB",
                                 wraplength=180, fg='white')

        self.button3b.config(state='normal')
        messagebox.showinfo("Sukses", f"Pesan berhasil diekstrak!\nTipe: {header['file_type']}\nUkuran: {len(data)} byte")

    def save_message(self):
        if self.extracted_data is None:
            messagebox.showerror("Error", "Tidak ada data untuk disimpan.")
            return

        ext = self.extracted_ext if self.extracted_ext else ".bin"
        save_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=self.extracted_fname,
            filetypes=[(ext.lstrip(".").upper() + " file", f"*{ext}"), ("All files", "*.*")]
        )
        if not save_path:
            return

        with open(save_path, 'wb') as f:
            f.write(self.extracted_data)

        messagebox.showinfo("Tersimpan", f"File disimpan ke:\n{save_path}")
