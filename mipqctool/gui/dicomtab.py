import os
import getpass
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from ..config import LOGGER
from ..dicomreport import DicomReport


class DicomTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__rootfolder = None
        self.__exportfolder = None
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
        self.tblabelframe.pack(fill='x', ipadx=4, ipady=4,
                               padx=4, pady=4)
        self.lbl_tag1.pack(anchor='w', padx=4)
        self.lbl_root_f.pack(fill='x', padx=4, pady=2)
        self.btn_root_f.pack(anchor='e', padx=4, pady=2)

        self.tblabelframe_output.pack(fill='x',
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
            self.__exportfolder = exportfolder
            self.lbl_report_f.config(text=exportfolder)

    def getrootfolder(self):
        rootfolder = tkfiledialog.askdirectory(title='Select DICOMs Root Folder')
        if rootfolder:
            self.__rootfolder = rootfolder
            self.lbl_root_f.config(text=rootfolder)

    def createreport(self):
        if not self.__rootfolder:
            tkmessagebox.showwarning('Can not create Report',
                                     'Please select DICOM folder first')
        elif not self.__exportfolder:
            tkmessagebox.showwarning('Can not create Report',
                                     'Please select Report Folder first')
        else:
            report = DicomReport(self.__rootfolder, getpass.getuser())
            report.writereport(self.__exportfolder)
            if self.isLoris.get():
                report.reorganizefiles(self.__exportfolder)
            tkmessagebox.showinfo(title='Status info',
                                  message='Reports have been created successully')
