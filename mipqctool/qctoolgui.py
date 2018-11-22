# simplegui.py python3
import tkinter as tk
from tkinter import ttk

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=0)

        self.create_widgets()

    def create_widgets(self):
        # Create a controller for tabs
        self.tabcontrol = ttk.Notebook(self.master)
        self.tabcontrol.pack(side='left', fill="both", expand=1)

        # Create the tab for tabular datasets processing
        self.tabframe = tk.Frame(self.tabcontrol)

        # Create a label frame where to put the input files interface
        self.tblabelframe = tk.LabelFrame(self.tabframe, text="Input")
        self.tblabelframe.pack(fill="both", expand="yes", ipadx=4, ipady=4,
                               padx=4, pady=4,)

        # Create labels for the input dataset files
        # Dataset file
        self.label_dataset = tk.Label(self.tblabelframe, text="Dataset file:")
        self.label_dataset.grid(row=0, column=0)
        self.label_dfilename = tk.Label(self.tblabelframe, text='Not selected',
                              bg='white', pady=4, width=50)
        self.label_dfilename.grid(row=0, column=1, pady=2)
        self.button_load_df = tk.Button(self.tblabelframe, text="select file")
        self.button_load_df.grid(row=0, column=2)

        # Metadata csv
        self.label_metadata = tk.Label(self.tblabelframe, text="Metadata file:")
        self.label_metadata.grid(row=1, column=0)
        self.label_mfilename = tk.Label(self.tblabelframe, text="Not selected",
                                        bg='white', pady=4, width=50)
        self.label_mfilename.grid(row=1, column=1, pady=2)
        self.button_load_md = tk.Button(self.tblabelframe, text="select file")
        self.button_load_md.grid(row=1, column=2)

        # Comumn patient id
        self.label_columnid = tk.Label(self.tblabelframe, text="Select id column:")
        self.label_columnid.grid(row=2, column=0)


        self.columnlist = ttk.Combobox(self.tblabelframe, width=50)
        self.columnlist.config(values=["Patient","Visit"])
        self.columnlist.grid(row=2, column=1, pady=4)

        self.button_save_tab = tk.Button(self.tabframe, text="Create Report")
        self.button_save_tab.pack(side='right')

        self.tabcontrol.add(self.tabframe, text="Tabular QC")


    def print_contents(self,event):
        print("hi. contents of entry is now ---->", self.contents.get())

root = tk.Tk()
app = Application(master = root)
app.master.title("Data Quality Control Tool")
app.master.resizable(False, False)
app.mainloop()
