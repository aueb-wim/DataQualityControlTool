import os
import csv
import json
from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from ..qcfrictionless import QcSchema, QcTable, FrictionlessFromDC
from ..tablereport import TableReport
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

        self.dataset_label = tk.Label(self, text='Dataset file:')
        self.datasetpath_label = tk.Label(self, text='Not selected',
                                          bg='white', pady=4, width=50)
        self.dload_button = tk.Button(self, text='Select File',
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
        self.save_button = tk.Button(self, text='Save Schema',
                                     command=self.save_schema)

    def __packing(self):

        self.dataset_label.grid(row=0, column=0, padx=2, sticky='e')
        self.dload_button.grid(row=0, column=2, sticky='w')
        self.datasetpath_label.grid(row=0, column=1, pady=2)

        # options section
        self.opts_lbframe.grid(row=1, column=1)
        self.categories_label.grid(row=1, column=0, sticky='e')
        self.categories_entry.grid(row=1, column=1, sticky='w')
        self.sample_rows_label.grid(row=2, column=0, sticky='e')
        self.sample_rows_entry.grid(row=2, column=1, sticky='w')
        self.save_button.grid(row=2, column=2, sticky='w')

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
