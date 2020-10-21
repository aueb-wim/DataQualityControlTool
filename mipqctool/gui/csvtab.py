import os
import csv
import json
from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from ..frictionlessfromdc import FrictionlessFromDC
from ..qcschema import QcSchema
from ..qctable import QcTable
from ..tablereport import TableReport
from ..exceptions import TableReportError
from ..config import LOGGER


class CsvTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # validation callback function for entering integer numbers
        self.int_validation = self.register(only_integers)
        # sample of rows for schema inferance variable 
        self.sample_rows = tk.StringVar()
        # maximum categories for schema inferance variable
        self.max_categories = tk.StringVar()
        self.__metafilepath = None
        self.__exportfiledir = None
        self.__datasetpath = None
        self.dname = None
        self.reportcsv = None
        self.cleaning = tk.BooleanVar()
        self.cleaning.set(False)
        self.infer = tk.BooleanVar()
        self.infer.set(False)
        self.json_type = tk.IntVar()
        # set default option for json metadata type to Frictionless
        self.json_type.set(1)
        self.json_types = [('Frictionless', 1), ('DataCatalogue', 2)]

        self.__init()
        self.__packing()

    def __init(self):
        self.tblabelframe = tk.LabelFrame(self, text='Dataset')

        # Input dataset interface
        # Dataset file (Labels and Button)
        self.d_dataset_label = tk.Label(self.tblabelframe, text='Dataset file:')
        self.d_datasetpath_label = tk.Label(self.tblabelframe, text='Not selected',
                                            bg='white', pady=4, width=50)
        self.d_columnid_label = tk.Label(self.tblabelframe, text='Select ColumnID:')
        self.d_headers_cbox = ttk.Combobox(self.tblabelframe, width=48)
        self.d_load_button = tk.Button(self.tblabelframe, text='Select File',
                                       command=self.loaddatasetfile)
        # Metadata csv (Labels and Button)
        self.m_tblabelframe = tk.LabelFrame(self, text='Metadata - Dataset\'s schema')
        #self.m_seperator = ttk.Separator(self.m_tblabelframe,
        #                                 orient=tk.HORIZONTAL)
        self.m_metadata_label = tk.Label(self.m_tblabelframe,
                                         text='Metadata (Schema) file:')
        self.m_metaname_label = tk.Label(self.m_tblabelframe, text='Not selected',
                                         bg='white', pady=4, width=25)
        self.m_metaload_button = tk.Button(self.m_tblabelframe, text='Select File',
                                           command=self.setmetadatafile)
        self.m_json_radiobutton1 = tk.Radiobutton(self.m_tblabelframe,
                                                  text='Frictionless',
                                                  padx=20,
                                                  variable=self.json_type,
                                                  value=1)
        self.m_json_radiobutton2 = tk.Radiobutton(self.m_tblabelframe,
                                                  text='DataCatalogue',
                                                  padx=20,
                                                  variable=self.json_type,
                                                  value=2)

        # Infer section
        self.i_categories_label = tk.Label(self.m_tblabelframe, text='Maximum Category Levels:')
        self.i_sample_rows_label = tk.Label(self.m_tblabelframe, text='Sample Rows:')
        self.i_categories_entry = tk.Entry(self.m_tblabelframe, width=10, 
                                           validate="key", textvariable=self.max_categories,
                                           validatecommand=(self.int_validation, '%S'))
        self.i_categories_entry.insert(0, '10')
        self.i_categories_entry.config(state='disabled')
        self.i_sample_rows_entry = tk.Entry(self.m_tblabelframe, width=10,
                                            validate="key", textvariable=self.sample_rows,
                                            validatecommand=(self.int_validation, '%S'))
        self.i_sample_rows_entry.insert(0, '100')
        self.i_sample_rows_entry.config(state='disabled')
        self.i_save_button = tk.Button(self.m_tblabelframe, text='Save Schema',
                                       state='disabled', command=self.save_schema)

        # No metadata file checkbox
        self.i_cbutton = tk.Checkbutton(self.m_tblabelframe,
                                        text='Infer schema',
                                        variable=self.infer,
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
        # Input dataset frame
        self.tblabelframe.pack(fill='both', expand='yes', ipadx=4, ipady=4,
                               padx=4, pady=4)
        self.d_dataset_label.grid(row=0, column=0, padx=2, sticky='e')
        self.d_load_button.grid(row=0, column=2, sticky='w')
        self.d_datasetpath_label.grid(row=0, column=1, pady=2)
        self.d_columnid_label.grid(row=1, column=0, padx=2, sticky='e')
        self.d_headers_cbox.grid(row=1, column=1, padx=2, pady=2)

        self.m_tblabelframe.pack(fill='both', expand='yes', ipadx=4, ipady=4,
                                 padx=4, pady=4)
        self.m_metadata_label.grid(row=0, column=0, padx=2, sticky='e')
        self.m_metaload_button.grid(row=0, column=2, sticky='w')
        self.m_metaname_label.grid(row=0, column=1, pady=2, padx=2)
        self.m_metaload_button.grid(row=0, column=2)
        self.m_json_radiobutton1.grid(row=0, column=3, sticky='w')
        self.m_json_radiobutton2.grid(row=1, column=3, sticky='w')
        #self.m_seperator.grid(row=2, column=0, columnspan=4, sticky='we', pady=2)

        # infer section
        self.i_categories_label.grid(row=2, column=0, sticky='e')
        self.i_categories_entry.grid(row=2, column=1, sticky='w')
        self.i_sample_rows_label.grid(row=3, column=0, sticky='e')
        self.i_sample_rows_entry.grid(row=3, column=1, sticky='w')
        self.i_cbutton.grid(row=2, column=2, sticky='w')
        self.i_save_button.grid(row=3, column=2, sticky='w')


        # Output frame
        self.tblabelframe_output.pack(fill='both', expand='yes',
                                      ipadx=4, ipady=4,
                                      padx=4, pady=4)
        self.label_export1.grid(row=0, column=0)
        self.label_export2.grid(row=0, column=1, padx=4)
        self.button_export_folder.grid(row=0, column=2, sticky='e')
        # Execution interface
        self.frame_exec.pack(fill='both', expand='yes',
                             padx=4, pady=4)
        self.frame_exec.grid_columnconfigure(0, weight=1)
        self.checkclean.grid(row=0, column=1, sticky='w')
        self.button_exec.grid(row=0, column=2, pady=4)

    def setmetadatafile(self):
        """Sets the filepath of the  metadata file """
        filepath = tkfiledialog.askopenfilename(title='select metadata file',
                                                filetypes=(('json files', '*.json'),
                                                           ('all files', '*.*')))
        if filepath:
            name = os.path.basename(filepath)
            self.m_metaname_label.config(text=name)
            self.__metafilepath = os.path.abspath(filepath)
        else:
            self.__metafilepath = None
            self.m_metaname_label.config(text='Not Selected')

    def loaddatasetfile(self):
        """Loads the dataset csv"""
        filepath = tkfiledialog.askopenfilename(title='select dataset file',
                                                filetypes=(('csv files', '*.csv'),
                                                           ('all files', '*.*')))
        if filepath:
            self.dname = os.path.basename(filepath)
            self.d_datasetpath_label.config(text=self.dname)
            self.datasetpath = filepath
            self.d_headers_cbox.delete(0, "end")
            with open(filepath, 'r') as csvfile:
                data = csv.DictReader(csvfile)
                self.d_headers_cbox.config(values=data.fieldnames)
        else:
            self.dname = None
            self.d_datasetpath_label.config(text='Not Selected')

    def setexportdir(self):
        """Folder path where the reports are stored"""
        filedir = tkfiledialog.askdirectory(title='Select folder to save report')
        if filedir:
            self.__exportfiledir = filedir
            self.label_export2.config(text=filedir)
        else:
            self.__exportfiledir = None
            self.label_export2.config(text='Not Selected')

    def createreport(self):
        LOGGER.info('Checking if the necessary fields are filled in...')
        warningtitle = 'Cannot create report'
        if not self.dname:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select dataset file')
        elif not self.d_headers_cbox.get():
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select ColumnID')
        # Case with metadata file available
        elif not self.infer.get() and not self.__metafilepath:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select metadata file')

        elif not self.__exportfiledir:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select export folder first')
        else:
            LOGGER.info('Everything looks ok...')
            filedir = self.__exportfiledir
            basename = os.path.splitext(self.dname)[0]
            pdfreportfile = os.path.join(filedir, basename + '_report.pdf')

            # Is metadata json file provided?
            if not self.infer.get():
                LOGGER.info('Using metadata file: %s' % self.__metafilepath)
                with open(self.__metafilepath) as json_file:
                    dict_schema = json.load(json_file)
                if self.json_type == 1:
                    dict_schema = FrictionlessFromDC(dict_schema).qcdescriptor
                schema = QcSchema(dict_schema)
                dataset = QcTable(self.datasetpath, schema=schema)

            # no? then try to infer the schema and save it in the same folder 
            else:
                max_categories = int(self.max_categories.get())
                sample_rows = int(self.sample_rows.get())
                dataset = QcTable(self.datasetpath, schema=None)
                dataset.infer(limit=sample_rows, maxlevels=max_categories)
                datasetfolder = os.path.dirname(self.datasetpath)
                metadatafile = os.path.join(datasetfolder, basename + '.json')
                dataset.schema.save(metadatafile)
            try:
                self.reportcsv = TableReport(dataset, id_column=self.d_headers_cbox.current())
                # Perform Data Cleaning?
                if self.cleaning.get():
                    self.reportcsv.apply_corrections()
                    self.reportcsv.save_corrected(self.datasetpath)

                # Create the pdf report
                self.reportcsv.printpdf(pdfreportfile)

                self.label_export2.config(text=filedir)
                tkmessagebox.showinfo(
                    title='Status info',
                    message='Reports have been created successully')

            except TableReportError:
                errortitle = 'Something went wrong!'
                tkmessagebox.showerror(errortitle, 'Please check metadata json')

    def save_schema(self):
        output_json = tkfiledialog.asksaveasfilename(title='enter file name',
                                                     filetypes=(('json files', '*.json'),
                                                                ('all files', '*.*')))
        if output_json:
            warningtitle = 'Can not save the json schema'
            if not self.dname:
                tkmessagebox.showwarning(warningtitle,
                                        'Please, select dataset file')
            max_categories = int(self.max_categories.get())
            sample_rows = int(self.sample_rows.get())
            dataset = QcTable(self.datasetpath, schema=None)
            dataset.infer(limit=sample_rows, maxlevels=max_categories)
            dataset.schema.save(output_json)

    def _metadata_check(self):
        if self.infer.get():
            status = 'disabled'
            entry_status = 'normal'
        else:
            status = 'normal'
            entry_status = 'disabled'
        self.m_metaload_button.config(state=status)
        self.m_metaname_label.config(state=status)
        self.i_categories_entry.config(state=entry_status)
        self.i_sample_rows_entry.config(state=entry_status)
        self.i_save_button.config(state=entry_status)


def only_integers(char):
    return char.isdigit()
