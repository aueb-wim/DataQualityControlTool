#!/usr/bin/env python3
import os
import csv
from tkinter import ttk
import pandas as pd
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from .qctablib import DatasetCsv, Metadata
from . import __version__

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=0)
        self.colval = None
        self.coltype = None
        self.metafilepath = None
        self.exportfiledir = None
        self.dataset = None
        self.dname = None
        self.reportcsv = None
        self.readable = tk.BooleanVar()
        self.readable.set(False)
        self.create_widgets()

    def create_widgets(self):
        """Draw the widgets"""
        # Create a controller for tabs
        self.tabcontrol = ttk.Notebook(self.master)
        self.tabcontrol.pack(side='left', fill="both", expand=1)

        # Create the tab for tabular datasets processing
        self.tabframe = tk.Frame(self.tabcontrol)

        # Input interface ###
        # Create a label frame where to put the input files interface
        self.tblabelframe = tk.LabelFrame(self.tabframe, text="Input")
        self.tblabelframe.pack(fill="both", expand="yes", ipadx=4, ipady=4,
                               padx=4, pady=4)
        # Dataset file (Labels and Button)
        self.label_dataset = tk.Label(self.tblabelframe, text="Dataset file:")
        self.label_dataset.grid(row=0, column=0)
        self.label_dfilename = tk.Label(self.tblabelframe, text='Not selected',
                                        bg='white', pady=4, width=50)
        self.label_dfilename.grid(row=0, column=1, pady=2)
        self.button_load_df = tk.Button(self.tblabelframe, text="Select File",
                                        command=self.loaddatasetfile)
        self.button_load_df.grid(row=0, column=2)
        # Metadata csv (Labels and Button)
        self.label_metadata = tk.Label(self.tblabelframe,
                                       text="Metadata file:")
        self.label_metadata.grid(row=1, column=0)
        self.label_mfilename = tk.Label(self.tblabelframe, text="Not selected",
                                        bg='white', pady=4, width=50)
        self.label_mfilename.grid(row=1, column=1, pady=2)
        self.button_load_md = tk.Button(self.tblabelframe, text="Select File",
                                        command=self.setmetadatafile)
        self.button_load_md.grid(row=1, column=2)
        # Select column for variable name (Label and dropdown list)
        self.label_columnvarname = tk.Label(self.tblabelframe,
                                            text="Select variable name column:")
        self.label_columnvarname.grid(row=2, column=0)
        self.colvallist = ttk.Combobox(self.tblabelframe, width=50)
        self.colvallist.config()
        self.colvallist.grid(row=2, column=1, pady=4)
        # Select column for variable type (Laber and dropdown list)
        self.label_columntype = tk.Label(self.tblabelframe,
                                         text="Select variable type column:")
        self.label_columntype.grid(row=3, column=0)
        self.coltypelist = ttk.Combobox(self.tblabelframe, width=50)
        self.coltypelist.config()
        self.coltypelist.grid(row=3, column=1, pady=4)

        # Output interface
        # Create a label frame where to put the output files interface
        self.tblabelframe_output = tk.LabelFrame(self.tabframe, text="Ouput")
        self.tblabelframe_output.pack(fill="both", expand="yes",
                                      ipadx=4, ipady=4,
                                      padx=4, pady=4)
        # Label for presenting the export folder
        self.label_export1 = tk.Label(self.tblabelframe_output,
                                      text="Output Folder:")
        self.label_export1.grid(row=0, column=0)
        self.label_export2 = tk.Label(self.tblabelframe_output,
                                      width=60, bg="white")
        self.label_export2.grid(row=0, column=1, padx=4)
        # Button Select export folder
        self.button_export_folder = tk.Button(self.tblabelframe_output,
                                              text="Select Folder",
                                              command=self.setexportdir)
        self.button_export_folder.grid(row=0, column=3, sticky='e')

        #  Execution interface
        self.frame_exec = tk.Frame(self.tabframe)
        self.frame_exec.pack(fill="both", expand="yes",
                             padx=4, pady=4)
        self.frame_exec.grid_columnconfigure(0, weight=1)

        # Checkbox readable columns in csv
        self.checkreadble = tk.Checkbutton(self.frame_exec,
                                           text="Readable columns",
                                           variable=self.readable)
        self.checkreadble.grid(row=0, column=1, sticky='w')
        # Button execution
        self.button_exec = tk.Button(self.frame_exec,
                                     text="Create Report",
                                     command=self.createreport)
        self.button_exec.grid(row=0, column=22, pady=4)

        # add the tab for tabular quality control into the main frame
        self.tabcontrol.add(self.tabframe, text="Tabular QC")

    def setmetadatafile(self):
        """Sets the filepath of the metadata file """
        filepath = tkfiledialog.askopenfilename(title="select metadata file",
                                                filetypes=(("csv files", "*.csv"),
                                                           ("all files", "*.*")))
        if filepath:
            name = os.path.basename(filepath)
            self.label_mfilename.config(text=name)
            with open(filepath, 'r') as meta:
                csvmeta = csv.DictReader(meta)
                self.colvallist.config(values=csvmeta.fieldnames)
                self.coltypelist.config(values=csvmeta.fieldnames)
            self.metafilepath = filepath
        else:
            self.metafilepath = None
            self.colvallist.config(values=None)
            self.coltypelist.config(values=None)
            self.label_mfilename.config(text='Not Selected')

    def loaddatasetfile(self):
        """Loads the dataset csv"""
        filepath = tkfiledialog.askopenfilename(title="select dataset file",
                                                filetypes=(("csv files", "*.csv"),
                                                           ("all files", "*.*")))
        if filepath:
            self.dname = os.path.basename(filepath)
            self.label_dfilename.config(text=self.dname)
            self.dataset = pd.read_csv(filepath)
        else:
            self.dname = None
            self.label_dfilename.config(text='Not Selected')

    def setexportdir(self):
        """Folder path where the reports are stored"""
        filedir = tkfiledialog.askdirectory(title="Select folder to save report")
        self.exportfiledir = filedir
        self.label_export2.config(text=filedir)

    def createreport(self):
        colval = self.colvallist.get()
        coltype = self.coltypelist.get()
        warningtitle = "Can not create report"
        if not self.dname:
            tkmessagebox.showwarning(warningtitle,
                                     "Please, select dataset file")
        elif not self.metafilepath:
            tkmessagebox.showwarning(warningtitle,
                                     "Please, select metadata file")
        elif colval == '' or coltype == '':
            tkmessagebox.showwarning(warningtitle,
                                     "Please, select metadata columns")
        elif not self.exportfiledir:
            tkmessagebox.showwarning(warningtitle,
                                     "Please, select export folder first")
        else:
            filedir = self.exportfiledir
            metadata = Metadata.from_csv(self.metafilepath, colval, coltype)
            basename = os.path.splitext(self.dname)[0]
            dreportfile = os.path.join(filedir,
                                       basename + "_dataset_report.csv")
            vreportfile = os.path.join(filedir, basename + "_report.csv")
            pdfreportfile = os.path.join(filedir, basename + "_report")
            self.reportcsv = DatasetCsv(self.dataset, self.dname, metadata)
            self.reportcsv.export_latex(pdfreportfile, pdf=True)
            self.reportcsv.export_dstat_csv(dreportfile, self.readable.get())
            self.reportcsv.export_vstat_csv(vreportfile, self.readable.get())
            self.label_export2.config(text=filedir)
            tkmessagebox.showinfo(title="Status info",
                message="Reports have been created successully")

def main():
    """Main application window"""
    root = tk.Tk()
    app = Application(master=root)
    app.master.title("HBP-MIP Data Quality Control Tool  version %s"
                     % __version__)
    app.master.resizable(False, False)
    app.mainloop()


if __name__ == '__main__':
    main()
