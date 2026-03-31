import tkinter as tk
from gui.transmitter import Transmitter
from gui.receiver import Receiver
from gui.change_page import change_page

class App(tk.Tk):
    def __init__(self):

        #config window
        super().__init__()
        self.geometry("720x640")
        self.resizable(False,False)
        self.title("Steganografi LSB")

        #icon window
        self.main_background_color = "#D9D9D9"
        self.icon = tk.PhotoImage(file='assets/icon.png')
        self.iconphoto(True,self.icon)
        self.config(background=self.main_background_color)

        #container
        container = tk.Frame(self,background=self.main_background_color)
        container.pack(expand=True, fill="both")

        #handler
        self.button_mode = change_page()

        #page
        self.trans_page = Transmitter(container, self.button_mode)
        self.rece_page  = Receiver(container, self.button_mode)

        self.trans_page.set_next_page(self.rece_page)
        self.rece_page.set_next_page(self.trans_page)

        self.button_mode.change_page(None, self.trans_page)


if __name__ == "__main__":
    app = App()
    app.mainloop()