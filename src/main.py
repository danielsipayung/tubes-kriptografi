import tkinter as tk
from gui.transmitter import Transmitter
from gui.receiver import Receiver

class App(tk.Tk):
    def __init__(self):
        #config window
        super().__init__()
        self.geometry("720x620")
        self.resizable(False,False)
        self.title("Steganografi LSB")

        #icon window
        main_background_color = '#d4d2d2'
        icon = tk.PhotoImage(file='assets\icon.png')
        self.iconphoto(True,icon)
        self.config(background=main_background_color)

        #container
        container = tk.Frame(self)
        container.pack(fill="y")

        #load page
        self.current_page = Transmitter(container)
        self.current_page = Receiver(container)
        self.current_page.pack(fill="both")



if __name__ == "__main__":
    app = App()
    app.mainloop()