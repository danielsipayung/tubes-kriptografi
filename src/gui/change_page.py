class change_page():

    def change_page(self, this_page, next_page):
        if this_page != None:
            this_page.pack_forget()
        if next_page != None:
            next_page.pack(expand=True, fill="both")