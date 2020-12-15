import os
import csv
import json
from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from ..qcfrictionless import QcSchema, QcTable, FrictionlessFromDC, CdeDict
from ..inferschema import InferSchema
from ..exceptions import TableReportError
from ..config import LOGGER


class InferTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # validation callback function for entering integer numbers
        self.int_validation = self.register(only_integers)
        # sample of rows for schema inferance variable 
        self.sample_rows = tk.StringVar()
        # maximum categories for schema inferance variable
        self.max_categories = tk.StringVar()
        self.__init()
        self.__packing()

    def __init(self):

        # Input dataset interface
        # Dataset file (Labels and Button)
        self.datasetframe = tk.Frame(self)
        self.dataset_label = tk.Label(self.datasetframe, text='Dataset file:')
        self.datasetpath_label = tk.Label(self.datasetframe, text='Not selected',
                                          bg='white', pady=4, width=50)
        self.dload_button = tk.Button(self.datasetframe, text='Select File',
                                      command=self.loaddatasetfile)

        self.opts_lbframe = tk.LabelFrame(self, text='Infer Options') 

        self.categories_label = tk.Label(self.opts_lbframe, text='Maximum Category Levels:')
        self.sample_rows_label = tk.Label(self.opts_lbframe, text='Sample Rows:')
        self.categories_entry = tk.Entry(self.opts_lbframe, width=10, 
                                         validate="key", textvariable=self.max_categories,
                                         validatecommand=(self.int_validation, '%S'))
        self.categories_entry.insert(0, '10')
        self.sample_rows_entry = tk.Entry(self.opts_lbframe, width=10,
                                          validate="key", textvariable=self.sample_rows,
                                          validatecommand=(self.int_validation, '%S'))
        self.sample_rows_entry.insert(0, '100')

        self.cde_dict_separator = ttk.Separator(self.opts_lbframe, orient='vertical')
        self.cde_dict_label2 = tk.Label(self.opts_lbframe, text = 'CDE suggestion (Optional)')
        self.cde_dict_label = tk.Label(self.opts_lbframe, text = 'No CDE Dictionary File Selected',
                                         width = 30, bg='white')
        self.cde_dict_button = tk.Button(self.opts_lbframe, text='Select file',
                                         command=self.load_cde_dict_file)

        self.save_button = tk.Button(self, text='Save Schema',
                                     command=self.save_schema)

    def __packing(self):

        self.datasetframe.pack(fill='both', ipady=2, ipadx=2)
        self.dataset_label.pack(side='left', padx=2)
        self.datasetpath_label.pack(side='left')
        self.dload_button.pack(side='left', pady=2, padx=4, anchor='e')


        # options section
        self.opts_lbframe.pack(fill='both', ipadx=2, ipady=2)
        self.categories_label.grid(row=0, column=0, sticky='e')
        self.categories_entry.grid(row=0, column=1, sticky='w')
        self.sample_rows_label.grid(row=1, column=0, sticky='e')
        self.sample_rows_entry.grid(row=1, column=1, sticky='w')
        self.cde_dict_separator.grid(row=0, column=2, rowspan=3, padx= 4, sticky="ns")
        self.cde_dict_label2.grid(row=0,column=3,pady=4, padx=4)
        self.cde_dict_label.grid(row=1,column=3,pady=4, padx=4)
        self.cde_dict_button.grid(row=1, column=4)
        self.save_button.pack(padx=4, anchor='e')

    def save_schema(self):
        output_file = tkfiledialog.asksaveasfilename(title='enter file name',
                                                     filetypes=(('excel files', '*.xlsx'),
                                                                ('all files', '*.*')))
        if output_file:
            warningtitle = 'Can not save the schema'
            if not self.dname:
                tkmessagebox.showwarning(warningtitle,
                                         'Please, select dataset file')
            max_categories = int(self.max_categories.get())
            sample_rows = int(self.sample_rows.get())
            dataset = QcTable(self.datasetpath, schema=None)
            if self.cde_dict:
                infer = InferSchema(dataset, self.dname, 
                                    sample_rows=sample_rows, maxlevels=max_categories,
                                    cdedict=self.cde_dict)
                infer.suggest_cdes()
                infer.export2excel(output_file)
  
            else: 
                infer = InferSchema(dataset, self.dname, 
                                    sample_rows=sample_rows, maxlevels=max_categories,
                                    cdedict=None)

                infer.export2excel(output_file)


    def loaddatasetfile(self):
        """Loads the dataset csv"""
        filepath = tkfiledialog.askopenfilename(title='select dataset file',
                                                filetypes=(('csv files', '*.csv'),
                                                           ('all files', '*.*')))
        if filepath:
            self.dname = os.path.basename(filepath)
            self.datasetpath_label.config(text=self.dname)
            self.datasetpath = filepath

        else:
            self.dname = None
            self.datasetpath_label.config(text='Not Selected')

    def load_cde_dict_file (self):
        filepath = tkfiledialog.askopenfilename(title='select cde dictionary file',
                                                filetypes=(('xlsx files', '*.xlsx'),
                                                           ('all files', '*.*')))
        if filepath:
            dict_name = os.path.basename(filepath)
            self.cde_dict_label.config(text=dict_name)
            self.cde_dict = CdeDict(filepath)


def only_integers(char):
    return char.isdigit()
