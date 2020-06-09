#!/usr/bin/env python3
import os
import csv
import json
import getpass
from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from .qcschema import QcSchema
from .qctable import QcTable
from .tablereport import TableReport
from .dicomreport import DicomReport
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
        self.tabcontrol.add(self.tabframe, text='Tabular QC')
        self.tabcontrol.add(self.tabframe2, text='Dicom QC')
        self.__packing()

    def __packing(self):
        """arrange the widgets"""
        self.pack(expand=0)
        self.tabcontrol.pack(side='left', fill='both', expand=1)


class CsvTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colval = None
        self.coltype = None
        self.metafilepath = None
        self.exportfiledir = None
        self.datasetpath = None
        self.dname = None
        self.reportcsv = None
        self.cleaning = tk.BooleanVar()
        self.nometadata = tk.BooleanVar()
        self.cleaning.set(False)
        self.__init()
        self.__packing()

    def __init(self):
        self.tblabelframe = tk.LabelFrame(self, text='Input')

        # Input interface
        # Dataset file (Labels and Button)
        self.label_dataset = tk.Label(self.tblabelframe, text='Dataset file:')
        self.label_dfilename = tk.Label(self.tblabelframe, text='Not selected',
                                        bg='white', pady=4, width=50)
        self.button_load_df = tk.Button(self.tblabelframe, text='Select File',
                                        command=self.loaddatasetfile)
        # Metadata csv (Labels and Button)
        self.label_metadata = tk.Label(self.tblabelframe,
                                       text='Metadata file:')
        self.label_mfilename = tk.Label(self.tblabelframe, text='Not selected',
                                        bg='white', pady=4, width=50)
        self.button_load_md = tk.Button(self.tblabelframe, text='Select File',
                                        command=self.setmetadatafile)

        # No metadata file checkbox
        self.checkmetadata = tk.Checkbutton(self.tblabelframe,
                                            text='No metadata file \n Infer json',
                                            variable=self.nometadata,
                                            command=self._metadata_check)

        # Output interface
        # Create a label frame where to put the output files interface
        self.tblabelframe_output = tk.LabelFrame(self, text='Ouput')
        # Label for presenting the export folder
        self.label_export1 = tk.Label(self.tblabelframe_output,
                                      text='Output Folder:')
        self.label_export2 = tk.Label(self.tblabelframe_output,
                                      width=60, bg='white')
        # Button Select export folder
        self.button_export_folder = tk.Button(self.tblabelframe_output,
                                              text='Select Folder',
                                              command=self.setexportdir)
        #  Execution interface
        self.frame_exec = tk.Frame(self)
        # Checkbox readable columns in csv
        self.checkclean = tk.Checkbutton(self.frame_exec,
                                         text='Perform Data Cleaning?',
                                         variable=self.cleaning)
        # Checkbox for producing a Latex instead a pdf file
        # self.checklatex = tk.Checkbutton(self.frame_exec,
        #                                 text='No pdf',
        #                                 variable=self.onlylatex)
        # Button execution
        self.button_exec = tk.Button(self.frame_exec,
                                     text='Create Report',
                                     command=self.createreport)

    def __packing(self):
        # Input frame
        self.tblabelframe.pack(fill='both', expand='yes', ipadx=4, ipady=4,
                               padx=4, pady=4)
        self.label_dataset.grid(row=0, column=0)
        self.button_load_df.grid(row=0, column=2)
        self.label_metadata.grid(row=1, column=0)
        self.label_dfilename.grid(row=0, column=1, pady=2)
        self.button_load_md.grid(row=1, column=2)
        self.checkmetadata.grid(row=1, column=3)
        self.label_mfilename.grid(row=1, column=1, pady=2)
        self.button_load_md.grid(row=1, column=2)

        # Output frame
        self.tblabelframe_output.pack(fill='both', expand='yes',
                                      ipadx=4, ipady=4,
                                      padx=4, pady=4)
        self.label_export1.grid(row=0, column=0)
        self.label_export2.grid(row=0, column=1, padx=4)
        self.button_export_folder.grid(row=0, column=3, sticky='e')
        # Execution interface
        self.frame_exec.pack(fill='both', expand='yes',
                             padx=4, pady=4)
        self.frame_exec.grid_columnconfigure(0, weight=1)
        self.checkclean.grid(row=0, column=1, sticky='w')
        # self.checklatex.grid(row=0, column=0, sticky='e')
        self.button_exec.grid(row=0, column=2, pady=4)

    def setmetadatafile(self):
        """Sets the filepath of the  metadata file """
        filepath = tkfiledialog.askopenfilename(title='select metadata file',
                                                filetypes=(('json files', '*.json'),
                                                           ('all files', '*.*')))
        if filepath:
            name = os.path.basename(filepath)
            self.label_mfilename.config(text=name)
            self.metafilepath = filepath
        else:
            self.metafilepath = None
            self.label_mfilename.config(text='Not Selected')

    def loaddatasetfile(self):
        """Loads the dataset csv"""
        filepath = tkfiledialog.askopenfilename(title='select dataset file',
                                                filetypes=(('csv files', '*.csv'),
                                                           ('all files', '*.*')))
        if filepath:
            self.dname = os.path.basename(filepath)
            self.label_dfilename.config(text=self.dname)
            self.datasetpath = filepath
        else:
            self.dname = None
            self.label_dfilename.config(text='Not Selected')

    def setexportdir(self):
        """Folder path where the reports are stored"""
        filedir = tkfiledialog.askdirectory(title='Select folder to save report')
        self.exportfiledir = filedir
        self.label_export2.config(text=filedir)

    def createreport(self):
        metadata = None
        warningtitle = 'Can not create report'
        if not self.dname:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select dataset file')
        # Case with metadata file available
        elif not self.nometadata.get():
            if not self.metafilepath:
                tkmessagebox.showwarning(warningtitle,
                                         'Please, select metadata file')

        elif not self.exportfiledir:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select export folder first')
        else:
            filedir = self.exportfiledir
            basename = os.path.splitext(self.dname)[0]
            pdfreportfile = os.path.join(filedir, basename + '_report.pdf')

            # Is metadata json file provided?
            if not self.nometadata.get():
                with open(self.metafilepath) as json_file:
                    dict_schema = json.load(json_file)
                    schema = QcSchema(dict_schema)
                    dataset = QcTable(self.datasetpath, schema=schema)
            # no? then try to infer the schema and save it in the same folder 
            else:
                dataset = QcTable(self.datasetpath, schema=None)
                dataset.infer()
                datasetfolder = os.path.dirname(self.datasetpath)
                metadatafile = os.path.join(datasetfolder, basename + '.json')
                dataset.schema.save(metadatafile)

            self.reportcsv = TableReport(dataset, id_column=1)
            # Perform Data Cleaning?
            if self.cleaning.get():
                self.reportcsv.apply_corrections()
                self.reportcsv.save_corrected(self.datasetpath)

            # Create the pdf report
            self.reportcsv.printpdf(pdfreportfile)

            self.label_export2.config(text=filedir)
            tkmessagebox.showinfo(title='Status info',
                message='Reports have been created successully')

    def _metadata_check(self):
        if self.nometadata.get():
            status = 'disabled'
        else:
            status = 'normal'
        self.button_load_md.config(state=status)
        self.label_mfilename.config(state=status)


class DicomTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rootfolder = None
        self.exportfolder = None
        self.isLoris = tk.BooleanVar()
        self.isLoris.set(False)
        self.__init()
        self.__packing()

    def __init(self):
        self.tblabelframe = tk.LabelFrame(self, text='Input')

        # Dataset file (Labels and Button)
        self.lbl_tag1 = tk.Label(self.tblabelframe, text='Dicom Root Folder:')
        self.lbl_root_f = tk.Label(self.tblabelframe, text='Not selected',
                                   bg='white')
        self.btn_root_f = tk.Button(self.tblabelframe, text='Select Folder',
                                    command=self.getrootfolder)
        # Output interface
        # Create a label frame where to put the output files interface
        self.tblabelframe_output = tk.LabelFrame(self, text='Output')
        # Label for presenting the export folder
        self.lbl_tag2 = tk.Label(self.tblabelframe_output,
                                 text='Output Report Folder:')
        self.lbl_report_f = tk.Label(self.tblabelframe_output,
                                     bg='white', text='Not selected')
        # Button Select export folder
        self.btn_report_f = tk.Button(self.tblabelframe_output,
                                      text='Select Folder',
                                      command=self.getexportfolder)

        # Lors pipeline checkbox
        self.chkb_loris = tk.Checkbutton(self.tblabelframe_output,
                                            text='Reorganize files for Loris pipeline?',
                                            variable=self.isLoris)

        # Button for creating the report
        self.btn_exec = tk.Button(self, text='Create Report',
                                  command=self.createreport)

    def __packing(self):
        self.tblabelframe.pack(fill='x', expand='yes', ipadx=4, ipady=4,
                               padx=4, pady=4)
        self.lbl_tag1.pack(anchor='w', padx=4)
        self.lbl_root_f.pack(fill='x', padx=4, pady=2)
        self.btn_root_f.pack(anchor='e', padx=4, pady=2)

        self.tblabelframe_output.pack(fill='x', expand='yes',
                                      ipadx=4, ipady=4,
                                      padx=4, pady=4)
        self.lbl_tag2.pack(anchor='w', padx=4)
        self.lbl_report_f.pack(fill='x', padx=4, pady=2)
        self.btn_report_f.pack(anchor='e', padx=4, pady=2)
        self.chkb_loris.pack(anchor='e', padx=4)
        self.btn_exec.pack(anchor='se', padx=4, pady=8)

    def getexportfolder(self):
        exportfolder = tkfiledialog.askdirectory(title='Select Report Folder')
        if exportfolder:
            if not os.path.isdir(exportfolder):
                os.mkdir(exportfolder)
            self.exportfolder = exportfolder
            self.lbl_report_f.config(text=exportfolder)

    def getrootfolder(self):
        rootfolder = tkfiledialog.askdirectory(title='Select DICOMs Root Folder')
        if rootfolder:
            self.rootfolder = rootfolder
            self.lbl_root_f.config(text=rootfolder)

    def createreport(self):
        if not self.rootfolder:
            tkmessagebox.showwarning('Can not create Report',
                                     'Please select DICOM folder first')
        elif not self.exportfolder:
            tkmessagebox.showwarning('Can not create Report',
                                     'Please select Report Folder first')
        else:
            report = DicomReport(self.rootfolder, getpass.getuser())
            report.writereport(self.exportfolder)
            if self.isLoris.get():
                report.reorganizefiles(self.exportfolder)
            tkmessagebox.showinfo(title='Status info',
                                  message='Reports have been created successully')


def main():
    """Main application window"""
    root = tk.Tk()
    app = Application(master=root)
    app.master.title('HBP-MIP Data Quality Control Tool  version %s'
                     % __version__)
    app.master.resizable(False, False)
    app.mainloop()


if __name__ == '__main__':
    main()
