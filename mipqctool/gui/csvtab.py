import os
import csv
import json

from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from mipqctool.gui.metadataframe import MetadataFrame
from mipqctool.gui.cleanwindow import CleanWindow
from mipqctool.controller import TableReport
from mipqctool.exceptions import TableReportError
from mipqctool.config import LOGGER

# TODO: make the selection of columnID optional
# 
class CsvTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.float_validation = self.register(is_number)
        # outlier threshold 
        self.outlier_threshold = tk.StringVar()
        self.__exportfiledir = None
        self.__datasetpath = None
        self.dname = None
        self.reportcsv = None
        # set default option for json metadata type to Frictionless
        self.report_type = tk.IntVar()
        self.report_type.set(1)
        self.report_types = [('Excel (xlsx)', 1), ('Pdf', 2)]

        self.__init()
        self.__packing()

    def __init(self):
        self.tblabelframe = tk.LabelFrame(self, text='Dataset')

        # Input dataset interface
        # Dataset file (Labels and Button)
        self.d_dataset_label = tk.Label(self.tblabelframe, text='Dataset file:')
        self.d_datasetpath_label = tk.Label(self.tblabelframe, text='Not selected',
                                            bg='white', pady=4, width=50)
        #self.d_columnid_label = tk.Label(self.tblabelframe, text='Select ColumnID:')
        #self.d_headers_cbox = ttk.Combobox(self.tblabelframe, width=48)
        self.d_load_button = tk.Button(self.tblabelframe, text='Select File',
                                       command=self.loaddatasetfile)
  
        self.md_frame = MetadataFrame(self)


        # Output interface
        # Create a label frame where to put the output files interface
        self.tblabelframe_output = tk.LabelFrame(self, text='Validation / Verification Report')
        # Label for presenting the export folder
        #self.label_export1 = tk.Label(self.tblabelframe_output,
        #                              text='Report Folder:')
        self.report_tblabelframe = tk.LabelFrame(self.tblabelframe_output,
                                                 text='Report Type:')
        self.report_radiobutton1 = tk.Radiobutton(self.report_tblabelframe,
                                                  text='Excel (xlsx)',
                                                  variable=self.report_type,
                                                  value=1)
        self.report_radiobutton2 = tk.Radiobutton(self.report_tblabelframe,
                                                  text='Pdf',
                                                  variable=self.report_type,
                                                  value=2)
        self.threshold_label1 = tk.Label(self.tblabelframe_output,
                                         text='Outlier Threshold (in Standard Deviations):')
        self.threshold_entry1 = tk.Entry(self.tblabelframe_output, width=5,
                                         validate="key", textvariable=self.outlier_threshold,
                                         validatecommand=(self.float_validation, '%P'))
        self.threshold_entry1.insert(0, '3')

        self.label_export2 = tk.Label(self.tblabelframe_output,
                                      width=45, bg='white',
                                      text='Not Selected')
        # Button Select export folder
        self.button_export_folder = tk.Button(self.tblabelframe_output,
                                              text='Select Folder',
                                              command=self.setexportdir)
        #  Execution interface
        self.frame_exec = tk.Frame(self)
        
        # Checkbox for producing a Latex instead a pdf file
        # self.checklatex = tk.Checkbutton(self.frame_exec,
        #                                 text='No pdf',
        #                                 variable=self.onlylatex)
        # Button execution
        self.button_exec = tk.Button(self.frame_exec,
                                     text='Create Report',
                                     command=self.createreport)

        self.show_sugg_button = tk.Button(self.frame_exec,
                                          text='Show cleaning suggestions',
                                          command=self.showsugg, state='disabled')
        self.clean_button = tk.Button(self.frame_exec, text='Perform Cleaning',
                                      command=self.cleandata, state='disabled')

    def __packing(self):
        # Input dataset frame
        self.tblabelframe.pack(fill='both', expand='yes', ipadx=4, ipady=4,
                               padx=4, pady=4)
        self.d_dataset_label.grid(row=0, column=0, padx=2, sticky='e')
        self.d_load_button.grid(row=0, column=2, sticky='w')
        self.d_datasetpath_label.grid(row=0, column=1, pady=2)
        #self.d_columnid_label.grid(row=1, column=0, padx=2, sticky='e')
        #self.d_headers_cbox.grid(row=1, column=1, padx=2, pady=2)

        # Metadata Frame
        self.md_frame.pack(fill='both')

        # Output Frame
        self.tblabelframe_output.pack(fill='both', expand='yes',
                                      ipadx=4, ipady=2)
        self.report_tblabelframe.grid(row=1, column=0, padx=4, pady=4, ipady=2)
        self.report_radiobutton1.pack(anchor='w', padx=4)
        self.report_radiobutton2.pack(anchor='w', padx=4)
        self.threshold_label1.grid(row=0, column=1, sticky='e')
        self.threshold_entry1.grid(row=0, column=2, sticky='w')
    
        #self.label_export1.grid(row=0, column=0)
        self.label_export2.grid(row=1, column=1, padx=4)
        self.button_export_folder.grid(row=1, column=2, sticky='e')
        # Execution interface
        self.frame_exec.pack(fill='both', expand='yes',
                             padx=4, pady=4)
        self.frame_exec.grid_columnconfigure(0, weight=1)
        self.button_exec.grid(row=0, column=2, pady=4)
        self.show_sugg_button.grid(row=1, column=1, pady=4)
        self.clean_button.grid(row=1, column=2, pady=4)

    def loaddatasetfile(self):
        """Loads the dataset csv"""
        filepath = tkfiledialog.askopenfilename(title='select dataset file',
                                                filetypes=(('csv files', '*.csv'),
                                                           ('all files', '*.*')))
        if filepath:
            self.dname = os.path.basename(filepath)
            self.d_datasetpath_label.config(text=self.dname)
            self.datasetpath = filepath
            #self.d_headers_cbox.delete(0, "end")
            #with open(filepath, 'r') as csvfile:
            #    data = csv.DictReader(csvfile)
            #    self.d_headers_cbox.config(values=data.fieldnames)
        else:
            self.dname = None
            self.d_datasetpath_label.config(text='Not Selected')
            #self.d_headers_cbox.delete(0, "end")

    def setexportdir(self):
        """Folder path where the reports are stored"""
        filedir = tkfiledialog.askdirectory(title='Select folder to save report')
        if filedir:
            self.__exportfiledir = filedir
            self.label_export2.config(text=filedir)
        else:
            self.__exportfiledir = None
            self.label_export2.config(text='Not Selected')

    def showsugg(self):
        CleanWindow(self)

    def cleandata(self):
        correctedcsvfile = tkfiledialog.asksaveasfilename(
            filetypes=(
                ("CSV files", "*.csv"), 
                ("All files", "*.*")
            )
        )
        if correctedcsvfile:
            self.reportcsv.apply_corrections()
            self.reportcsv.save_corrected(correctedcsvfile)
        else:
            tkmessagebox.showwarning('Warning!',
                                     'Please, select file location!')

    def createreport(self):
        LOGGER.info('Checking if the necessary fields are filled in...')
        warningtitle = 'Cannot create report'
        if not self.dname:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select dataset file')
        #elif not self.d_headers_cbox.get():
        #    tkmessagebox.showwarning(warningtitle,
        #                             'Please, select ColumnID')
        elif self.md_frame.from_disk.get() and not self.md_frame.metafilepath:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select metadata file')
        elif self.md_frame.from_dc.get() and not self.md_frame.dc_json:
            tkmessagebox.showwarning(warningtitle,
                                     'Could not get metadata from Data Cataloge')

        elif not self.__exportfiledir:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select export folder first')
        else:
            try:
                threshold = float(self.outlier_threshold.get())
                LOGGER.info('Outlier threshold: %s' % self.outlier_threshold.get())
            except ValueError:
                LOGGER.warning('Could not retrieve outlier threshold. \
                                Setting it to default value: 3')
                threshold = 3
            LOGGER.info('Everything looks ok...')
            filedir = self.__exportfiledir
            basename = os.path.splitext(self.dname)[0]
            pdfreportfile = os.path.join(filedir, basename + '_report.pdf')
            xlsxreportfile = os.path.join(filedir, basename + '_report.xlsx')
            schema_type = 'qc'

            if self.md_frame.from_disk.get():
                LOGGER.info('Retrieving Metadata from localdisk...')
                LOGGER.info('Using metadata file: %s' % self.md_frame.metafilepath)
                with open(self.md_frame.metafilepath) as json_file:
                    dict_schema = json.load(json_file)
                if self.md_frame.json_type == 1:
                    schema_type = 'dc'

            elif self.md_frame.from_dc.get():
                LOGGER.info('Retrieving Metadata from Data Catalogue...')
                LOGGER.info('Selected pathology is {}, CDE version: {}'.format(
                    self.md_frame.selected_pathology.get(),                                              
                    self.md_frame.selected_version.get())
                )             
                dict_schema = self.md_frame.dc_json
                schema_type = 'dc'

            try:
                self.reportcsv = TableReport.from_disc(self.datasetpath,
                                                       dict_schema=dict_schema,
                                                       schema_type=schema_type,                                                      
                                                       threshold=threshold)#id_column=self.d_headers_cbox.current())
                if self.reportcsv.isvalid:
                    LOGGER.info('The dataset has is valid.')
                else:
                    LOGGER.info('CAUTION! The dataset is invalid!')

                # Perform Data Cleaning?
                #if self.cleaning.get():
                 #   self.reportcsv.apply_corrections()

                    #self.reportcsv.save_corrected(correctedcsvfile)

                # Create the  report
                if self.report_type.get() == 1:
                    self.reportcsv.printexcel(xlsxreportfile)
                else:
                    self.reportcsv.printpdf(pdfreportfile)

                self.label_export2.config(text=filedir)
                tkmessagebox.showinfo(
                    title='Status info',
                    message='Reports have been created successully'
                )

                self.show_sugg_button.config(state='normal')
                self.clean_button.config(state='normal')

            except TableReportError:
                errortitle = 'Something went wrong!'
                tkmessagebox.showerror(errortitle, 'Please check metadata json')
	
def is_number(s):
    if s == '':
        return True
    try:
        float(s)
    except ValueError:
        return False
    return True
