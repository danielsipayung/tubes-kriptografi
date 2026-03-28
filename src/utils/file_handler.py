from tkinter import filedialog

class File_handler:
    def open_file(self):
        file_input = filedialog.askopenfilename()
        print(file_input)

    def save_file(self):
        file_output = filedialog.asksaveasfile(defaultextension='.txt',
                                               filetypes=[
                                                   ("Text",".txt"),
                                                   ("Video",".avi"),
                                                   ("Image",".jpg")
                                               ])
        file_output.write("test")
        file_output.close()