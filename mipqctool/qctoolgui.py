#!/usr/bin/env python3
import os
import csv
import getpass
from tkinter import ttk
import pandas as pd
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from .qctablib import DatasetCsv, Metadata
from .qcdicom import DicomReport
from . import __version__

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.__init()


    def __init(self):
        """Draw the widgets"""
        # Create a controller for tabs
        self.tabcontrol = ttk.Notebook(self.master)
        # Create the tab for tabular datasets processing
        self.tabframe = CsvTab()
        self.tabframe2 = DicomTab()

        # add the tab for tabular quality control into the main frame
        self.tabcontrol.add(self.tabframe, text="Tabular QC")
        self.tabcontrol.add(self.tabframe2, text="Dicom QC")
        self.__packing()

    def __packing(self):
        """arrange the widgets"""
        self.pack(expand=0)
        self.tabcontrol.pack(side='left', fill="both", expand=1)



class CsvTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colval = None
        self.coltype = None
        self.metafilepath = None
        self.exportfiledir = None
        self.dataset = None
        self.dname = None
        self.reportcsv = None
        self.readable = tk.BooleanVar()
        self.onlylatex = tk.BooleanVar()
        self.nometadata = tk.BooleanVar()
        self.readable.set(False)
        self.onlylatex.set(False)
        self.__init()
        self.__packing()

    def __init(self):
        self.tblabelframe = tk.LabelFrame(self, text="Input")

        # Input interface
        # Dataset file (Labels and Button)
        self.label_dataset = tk.Label(self.tblabelframe, text="Dataset file:")
        self.label_dfilename = tk.Label(self.tblabelframe, text='Not selected',
                                        bg='white', pady=4, width=50)
        self.button_load_df = tk.Button(self.tblabelframe, text="Select File",
                                        command=self.loaddatasetfile)
        # Metadata csv (Labels and Button)
        self.label_metadata = tk.Label(self.tblabelframe,
                                       text="Metadata file:")
        self.label_mfilename = tk.Label(self.tblabelframe, text="Not selected",
                                        bg='white', pady=4, width=50)
        self.button_load_md = tk.Button(self.tblabelframe, text="Select File",
                                        command=self.setmetadatafile)
        # Select column for variable name (Label and dropdown list)
        self.label_columnvarname = tk.Label(self.tblabelframe,
                                            text="Select variable name column:")
        self.colvallist = ttk.Combobox(self.tblabelframe, width=50)
        self.colvallist.config()
        # Select column for variable type (Laber and dropdown list)
        self.label_columntype = tk.Label(self.tblabelframe,
                                         text="Select variable type column:")
        self.coltypelist = ttk.Combobox(self.tblabelframe, width=50)
        self.coltypelist.config()
        # No metadata file checkbox
        self.checkmetadata = tk.Checkbutton(self.tblabelframe,
                                            text="No metadata file",
                                            variable=self.nometadata,
                                            command=self._metadata_check)

    
        # Output interface
        # Create a label frame where to put the output files interface
        self.tblabelframe_output = tk.LabelFrame(self, text="Ouput")
        # Label for presenting the export folder
        self.label_export1 = tk.Label(self.tblabelframe_output,
                                      text="Output Folder:")
        self.label_export2 = tk.Label(self.tblabelframe_output,
                                      width=60, bg="white")
        # Button Select export folder
        self.button_export_folder = tk.Button(self.tblabelframe_output,
                                              text="Select Folder",
                                              command=self.setexportdir)
        #  Execution interface
        self.frame_exec = tk.Frame(self)
        # Checkbox readable columns in csv
        self.checkreadble = tk.Checkbutton(self.frame_exec,
                                           text="Readable columns",
                                           variable=self.readable)
        # Checkbox for producing a Latex instead a pdf file
        self.checklatex = tk.Checkbutton(self.frame_exec,
                                         text="No pdf",
                                         variable=self.onlylatex)
        # Button execution
        self.button_exec = tk.Button(self.frame_exec,
                                     text="Create Report",
                                     command=self.createreport)

    def __packing(self):
        # Input frame
        self.tblabelframe.pack(fill="both", expand="yes", ipadx=4, ipady=4,
                               padx=4, pady=4)
        self.label_dataset.grid(row=0, column=0)
        self.button_load_df.grid(row=0, column=2)
        self.label_metadata.grid(row=1, column=0)
        self.label_dfilename.grid(row=0, column=1, pady=2)
        self.button_load_md.grid(row=1, column=2)
        self.checkmetadata.grid(row=5, column=2)
        self.label_mfilename.grid(row=1, column=1, pady=2)
        self.button_load_md.grid(row=1, column=2)
        self.colvallist.grid(row=2, column=1, pady=4)
        self.label_columnvarname.grid(row=2, column=0)
        self.label_columntype.grid(row=3, column=0)
        self.coltypelist.grid(row=3, column=1, pady=4)
        # Output frame
        self.tblabelframe_output.pack(fill="both", expand="yes",
                                      ipadx=4, ipady=4,
                                      padx=4, pady=4)
        self.label_export1.grid(row=0, column=0)
        self.label_export2.grid(row=0, column=1, padx=4)
        self.button_export_folder.grid(row=0, column=3, sticky='e')
        # Execution interface
        self.frame_exec.pack(fill="both", expand="yes",
                             padx=4, pady=4)
        self.frame_exec.grid_columnconfigure(0, weight=1)
        self.checkreadble.grid(row=0, column=1, sticky='w')
        self.checklatex.grid(row=0, column=0, sticky='e')
        self.button_exec.grid(row=0, column=2, pady=4)

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
        metadata = None
        colval = self.colvallist.get()
        coltype = self.coltypelist.get()
        warningtitle = "Can not create report"
        if not self.dname:
            tkmessagebox.showwarning(warningtitle,
                                     "Please, select dataset file")
        # Case with metadata file available                             
        elif not self.nometadata.get():
            if not self.metafilepath:
                tkmessagebox.showwarning(warningtitle,
                                         "Please, select metadata file")
            elif colval == '' or coltype == '':
                tkmessagebox.showwarning(warningtitle,
                                        "Please, select metadata columns")
            metadata = Metadata.from_csv(self.metafilepath, colval, coltype)

        elif not self.exportfiledir:
            tkmessagebox.showwarning(warningtitle,
                                     "Please, select export folder first")
        else:
            filedir = self.exportfiledir
            basename = os.path.splitext(self.dname)[0]
            dreportfile = os.path.join(filedir,
                                       basename + "_dataset_report.csv")
            vreportfile = os.path.join(filedir, basename + "_report.csv")
            pdfreportfile = os.path.join(filedir, basename + "_report")
            self.reportcsv = DatasetCsv(self.dataset, self.dname, metadata)
            self.reportcsv.export_dstat_csv(dreportfile, self.readable.get())
            self.reportcsv.export_vstat_csv(vreportfile, self.readable.get())
            self.reportcsv.export_latex(pdfreportfile, pdf=not self.onlylatex.get())
            self.label_export2.config(text=filedir)
            tkmessagebox.showinfo(title="Status info",
                message="Reports have been created successully")

    def _metadata_check(self):
        if self.nometadata.get():
            status = 'disabled'
        else:
            status = 'normal'
        self.button_load_md.config(state=status)
        self.coltypelist.config(state=status)
        self.colvallist.config(state=status)
        self.label_mfilename.config(state=status)

class DicomTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rootfolder = None
        self.__init()
        self.__packing()

    def __init(self):
        self.tblabelframe = tk.LabelFrame(self, text="Input")

        # Dataset file (Labels and Button)
        self.lbl_tag1 = tk.Label(self.tblabelframe, text="Dicom Root Folder:")
        self.lbl_root_f = tk.Label(self.tblabelframe, text='Not selected',
                                   bg='white', width=85)
        self.btn_root_f= tk.Button(self.tblabelframe, text="Select Folder",
                                   command = self.getrootfolder)
        # Output interface
        # Create a label frame where to put the output files interface
        self.tblabelframe_output = tk.LabelFrame(self, text="Ouput")
        # Label for presenting the export folder
        self.lbl_tag2 = tk.Label(self.tblabelframe_output,
                                 text="Output Excel File:")
        self.lbl_report_f = tk.Label(self.tblabelframe_output,
                                     width=85, bg="white")
        # Button Select export file
        self.btn_report_f = tk.Button(self,
                                      text="Create Report",
                                      command=self.createreport)

    def __packing(self):
        self.tblabelframe.pack(fill="both", expand="yes", ipadx=4, ipady=4,
                               padx=4, pady=4)
        self.lbl_tag1.grid(row=0, column=0, padx=4, sticky='w')
        self.lbl_root_f.grid(row=1, column=0, padx=5, pady=4)
        self.btn_root_f.grid(row=2, column=0, padx=4,
                             pady=4, sticky='se')

        self.tblabelframe_output.pack(fill="both", expand="yes",
                                      ipadx=4, ipady=4,
                                      padx=4, pady=4)
        self.lbl_tag2.grid(row=0, column=0, padx=2, sticky='w')
        self.lbl_report_f.grid(row=1, column=0, padx=2)
        self.btn_report_f.pack(anchor='e', pady=4, padx=4)

    def getrootfolder(self):
        rootfolder = tkfiledialog.askdirectory(title="Select DICOMs Root Folder")
        if rootfolder:
            self.rootfolder = rootfolder
            self.lbl_root_f.config(text=rootfolder)

    def createreport(self):
        if not self.rootfolder:
            tkmessagebox.showwarning('Can not create Report',
                                     'Please select DICOM folder first')
        else:
            excelfile = tkfiledialog.asksaveasfilename(title='Save',
                                                       filetypes=[('Excel files', '*.xls')],
                                                       defaultextension='.xls')
            if excelfile:
                dicom_json = os.path.join(DIR_PATH, 'data', 'dicom-schema.json')
                report = DicomReport(self.rootfolder, getpass.getuser(),dicom_json)
                report.export2xls(excelfile)
                self.lbl_report_f.config(text=excelfile)
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
