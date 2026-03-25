from tkinter import filedialog

class File_handler:
    def open_file(self):
        file_input = filedialog.askopenfilename()
        print(file_input)