import tkinter as tk
from tkinter import messagebox, filedialog
import os, json, threading, shutil

from gui.change_page import change_page
from utils.file_handler import File_handler
from steganography.avi_process import AviProcess, BASE_DIR
from steganography.text_file_binary import BinaryConverter
from steganography.steganography import Steganography
from crypto.a51 import A51
from utils.video_comparator import compare_videos_returns, show_histograms
from tkvideo import tkvideo

FRAMES_FOLDER = "Gyokeres"
OUTPUT_PATH = os.path.join(BASE_DIR, "output", "stegovid.avi")


class Transmitter(tk.Frame):
    def __init__(self, container, handler):
        super().__init__(container, bg='#D9D9D9')

        self.handler = handler
        self.next_page = None
        self.path  = File_handler()
        self.avi   = AviProcess()
        self.conv  = BinaryConverter()
        self.stega = Steganography()

        self.video_path = None
        self.message_path = None
        self.current_fps = 30.0
        self.stego_output_path = None

        frame1 = tk.Frame(self, bg='#D9D9D9')
        embed_button = tk.Button(frame1, text='EMBED', fg='white', bg='#35915B',
                                 width=13, font=("Arial", 10, "bold"), relief=tk.FLAT)
        extract_button = tk.Button(frame1, text='EXTRACT', fg='white', bg='#D58B1B',
                                   width=13, font=("Arial", 10, "bold"), relief=tk.FLAT,
                                   command=lambda: self.handler.change_page(self, self.next_page))
        frame1.pack(fill='both', pady=10)
        embed_button.pack(side='left', ipady=6, ipadx=7, padx=10)
        extract_button.pack(side='left', ipady=6, ipadx=7)

        frame2 = tk.Frame(self, bg='#D9D9D9')
        tk.Label(frame2, text='Transmitter', font=("Arial", 20, "bold"), bg='#D9D9D9').pack(anchor='w')
        frame2.pack(fill='both', pady=8, padx=(10, 0))

        frame3 = tk.Frame(self, bg="#FFFFFF")

        frame3a = tk.Frame(frame3, bg="#53B27B")
        tk.Label(frame3a, text='Cover Video', font=("Arial", 16, "bold"), bg='#35915B', fg='white').pack(fill='both')
        self.label3a1 = tk.Label(frame3a, text='Video', font=("Arial", 16, "bold"), bg="#000000", pady=6)
        self.label3a1.pack(fill='both', ipady=0)
        tk.Button(frame3a, text='Select file', font=("Arial", 10, "bold"), fg='white',
                  bg="#982011", pady=3, relief=tk.FLAT, command=self.pick_file).pack(ipadx=10, pady=5)

        self.frame3b = tk.Frame(frame3, bg="#53B27B")
        tk.Label(self.frame3b, text='Secret Message', font=("Arial", 16, "bold"), bg='#35915B', fg='white').pack(fill='both')
        self.label3b1 = tk.Label(self.frame3b, text=' ', font=("Arial", 12, "bold"), bg="#000000", fg='white', pady=6)
        self.label3b1.pack(fill='both', ipady=39)
        tk.Button(self.frame3b, text='Select file', font=("Arial", 10, "bold"), fg='white',
                  bg='#982011', pady=3, relief=tk.FLAT, command=self.pick_file2).pack(ipadx=10, pady=5)

        frame3c = tk.Frame(frame3, bg="#B9BB11")
        tk.Label(frame3c, text='Stego Video', font=("Arial", 16, "bold"), bg="#B9BB11", fg='white').pack(fill='both')
        self.label3c1 = tk.Label(frame3c, text='Video', font=("Arial", 16, "bold"), bg="#000000", pady=6)
        self.label3c1.pack(fill='both', ipady=40)
        self.button3c = tk.Button(frame3c, text='Save', font=("Arial", 10, "bold"), fg='white',
                                  bg='#111111', pady=3, relief=tk.FLAT, command=self.save_stego,
                                  highlightbackground="white", state='disabled')
        self.button3c.pack(ipadx=10, pady=5)

        frame3.pack(fill='both')
        frame3a.pack(side='left', fill='both', expand=True)
        self.frame3b.pack(side='left', fill='both', expand=True)
        frame3c.pack(side='left', fill='both', expand=True)

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
        tk.Button(self, text='Embed Message', font=("Arial", 12, "bold"),
                  bg='#947A1D', fg='white', relief=tk.FLAT,
                  command=self.embed).pack(ipady=6, ipadx=80, padx=10)

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

    def pick_file(self):
        file_name = self.path.open_file()
        if not file_name:
            return
        self.video_path = file_name
        self.label3a1.config(text="Mengekstrak frame...", bg='#333333', fg='white')

        def _run():
            try:
                self.current_fps = self.avi.extract_frames(file_name, FRAMES_FOLDER)
                self.after(0, lambda: self.start_video_preview(file_name))
            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Error", f"Gagal ekstrak frame: {err}"))

        threading.Thread(target=_run, daemon=True).start()

    def pick_file2(self):
        file_path = self.path.open_file()
        if file_path:
            self.message_path = file_path
            self.label3b1.config(text=f"Message: {os.path.basename(file_path)}")

    def start_video_preview(self, path):
        self.player = tkvideo(path, self.label3a1, loop=1, size=(192, 108))
        self.player.play()

    def start_stego_preview(self, path):
        self.stego_player = tkvideo(path, self.label3c1, loop=1, size=(192, 108))
        self.stego_player.play()

    def embed(self):
        if not self.video_path:
            messagebox.showerror("Error", "Pilih cover video terlebih dahulu.")
            return
        if not self.message_path:
            messagebox.showerror("Error", "Pilih secret message terlebih dahulu.")
            return

        mode = self.var2.get()
        stego_key = self.entry7.get().strip() if mode == "random" else None
        use_enc = self.use_encryption.get()
        a51_key = self.entry5.get().strip() if use_enc else None

        if mode == "random" and not stego_key:
            messagebox.showerror("Error", "Masukkan stego key untuk mode random.")
            return
        if use_enc and not a51_key:
            messagebox.showerror("Error", "Masukkan A5/1 key untuk enkripsi.")
            return

        frames_path = os.path.join(BASE_DIR, "avi_frames", FRAMES_FOLDER)
        if not os.path.exists(frames_path):
            messagebox.showerror("Error", "Frame folder tidak ditemukan. Pilih ulang cover video.")
            return

        self.button3c.config(state='disabled')
        self.label3c1.config(text="Menyematkan pesan...", bg='#333333', fg='white')

        def _run():
            try:
                frame_order = self.stega.get_sorted_frame_order(frames_path)
                if not frame_order:
                    raise ValueError("Tidak ada frame ditemukan di folder.")

                filename = os.path.basename(self.message_path)
                extension = ("." + filename.split('.')[-1]) if "." in filename else ""
                with open(self.message_path, 'rb') as f:
                    data_bytes = f.read()

                binary_data = ''.join(format(b, '08b') for b in data_bytes)

                if use_enc:
                    cipher = A51(a51_key)
                    encrypted_bits = cipher.enc_block([int(b) for b in binary_data])
                    binary_data = ''.join(map(str, encrypted_bits))

                header_dict = {
                    "file_type": "file",
                    "extension": extension,
                    "file_size": len(binary_data),
                    "filename": filename,
                    "encrypted": use_enc,
                    "embed_process": mode,
                }
                header_str = json.dumps(header_dict) + Steganography.DELIMITER
                binary_header = ''.join(format(ord(c), '08b') for c in header_str)
                payload = binary_header + binary_data

                self.stega.embed_secret(payload, frames_path, frame_order, mode=mode, stego_key=stego_key)

                os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
                self.avi.rebuild_video(FRAMES_FOLDER, OUTPUT_PATH, self.current_fps)
                self.stego_output_path = OUTPUT_PATH

                self.after(0, self._finish_embed)

            except Exception as e:
                self.after(0, lambda err=e: (
                    messagebox.showerror("Error", str(err)),
                    self.label3c1.config(text="Error", bg="#000000", fg="red")
                ))

        threading.Thread(target=_run, daemon=True).start()

    def _finish_embed(self):
        self.button3c.config(state='normal')
        self.start_stego_preview(self.stego_output_path)
        messagebox.showinfo("Sukses", "Pesan berhasil disematkan ke stego video!")
        self._run_comparison()

    def _run_comparison(self):
        orig = self.video_path
        stego = self.stego_output_path

        loading = tk.Toplevel(self)
        loading.title("Membandingkan Video...")
        loading.configure(bg='#D9D9D9')
        loading.resizable(False, False)
        tk.Label(loading, text="Sedang membandingkan video...",
                 font=("Arial", 11), bg='#D9D9D9', padx=24, pady=20).pack()
        loading.lift()
        loading.focus_force()

        def _run():
            try:
                stats, frame_out = compare_videos_returns(orig, stego)
                self.after(0, lambda s=stats, f=frame_out: (
                    loading.destroy(),
                    self._show_comparison(s, f)
                ))
            except Exception as e:
                self.after(0, lambda err=e: (
                    loading.destroy(),
                    messagebox.showerror("Comparator Error", str(err))
                ))

        threading.Thread(target=_run, daemon=True).start()

    def _show_comparison(self, stats, frame_out):
        win = tk.Toplevel(self)
        win.title("Video Comparison — MSE & PSNR")
        win.configure(bg='#D9D9D9')
        win.resizable(False, False)
        win.lift()
        win.focus_force()

        mean_mse = stats["Mean MSE"]
        valid_psnr = [p for p in stats["psnr"] if p != float('inf')]
        mean_psnr = sum(valid_psnr) / len(valid_psnr) if valid_psnr else float('inf')
        changed = sum(1 for m in stats["mse"] if m != 0)
        total = len(stats["mse"])

        tk.Label(win, text="Hasil Perbandingan Video",
                 font=("Arial", 14, "bold"), bg='#D9D9D9').pack(pady=(16, 8))

        grid = tk.Frame(win, bg='#D9D9D9')
        grid.pack(padx=24, pady=4)

        rows = [
            ("Total frame",   f"{total}"),
            ("Frame berubah", f"{changed}"),
            ("Mean MSE",      f"{mean_mse:.6f}"),
            ("Mean PSNR",     f"{mean_psnr:.4f} dB"),
        ]
        for i, (label, value) in enumerate(rows):
            tk.Label(grid, text=label + ":", font=("Arial", 11), bg='#D9D9D9',
                     anchor='w', width=16).grid(row=i, column=0, sticky='w', pady=2)
            tk.Label(grid, text=value, font=("Arial", 11, "bold"),
                     bg='#D9D9D9', anchor='w').grid(row=i, column=1, sticky='w', padx=(8, 0))

        btn_frame = tk.Frame(win, bg='#D9D9D9')
        btn_frame.pack(pady=16)

        if frame_out[0]:
            tk.Button(btn_frame, text="Tampilkan Histogram",
                      font=("Arial", 10, "bold"), bg='#35915B', fg='white',
                      relief=tk.FLAT, padx=10, pady=4,
                      command=lambda: threading.Thread(
                          target=show_histograms, args=(frame_out,), daemon=True).start()
                      ).pack(side='left', padx=8)

        tk.Button(btn_frame, text="Tutup", font=("Arial", 10, "bold"),
                  bg='#982011', fg='white', relief=tk.FLAT, padx=10, pady=4,
                  command=win.destroy).pack(side='left', padx=8)

    def save_stego(self):
        if not self.stego_output_path or not os.path.exists(self.stego_output_path):
            messagebox.showerror("Error", "Belum ada stego video yang dibuat.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".avi",
            initialfile="stegovid.avi",
            filetypes=[("AVI video", "*.avi"), ("All files", "*.*")]
        )
        if not save_path:
            return

        shutil.copy2(self.stego_output_path, save_path)
        messagebox.showinfo("Tersimpan", f"Stego video disimpan ke:\n{save_path}")
