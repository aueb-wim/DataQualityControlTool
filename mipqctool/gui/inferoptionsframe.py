import os

from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from mipqctool.model.qcfrictionless import CdeDict

class InferOptionsFrame(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thresholdstring = tk.StringVar()
        self.na_empty_strings_only=tk.BooleanVar()
        self.threshold_validation = self.register(valid_threshold)
        self.cde_dict = None
        # validation callback function for entering integer numbers
        self.int_validation = self.register(only_integers)
        # sample of rows for schema inferance variable 
        self.sample_rows = tk.StringVar()
        # maximum categories for schema inferance variable
        self.max_categories = tk.StringVar()
        self.__init()
        self.__packing()

    def __init(self):
        self.opts_lbframe = tk.LabelFrame(self, text='Infer Options')

        self.categories_label = tk.Label(self.opts_lbframe, text='Maximum Category Levels:')
        self.sample_rows_label = tk.Label(self.opts_lbframe, text='Sample Rows:')
        self.categories_entry = tk.Entry(self.opts_lbframe, width=10, 
                                         validate="key", textvariable=self.max_categories,
                                         validatecommand=(self.int_validation, '%S'))
        self.categories_entry.insert(0, '10')
        self.sample_rows_entry = tk.Entry(self.opts_lbframe, width=10,
                                          validate='key', textvariable=self.sample_rows,
                                          validatecommand=(self.int_validation, '%S'))
        self.sample_rows_entry.insert(0, '100')

        self.na_option_chbutton = tk.Checkbutton(self.opts_lbframe, text='Only infer empty strings as NAs',
                                                 var=self.na_empty_strings_only)

        self.cde_dict_separator = ttk.Separator(self.opts_lbframe, orient='vertical')
        self.cde_dict_label2 = tk.Label(self.opts_lbframe, text='CDE suggestion (Optional)')
        self.cde_threshold_label = tk.Label(self.opts_lbframe, text='Similarity Threshold (0.0 - 1.0)')
        self.cde_threshold_entry = tk.Entry(self.opts_lbframe, width=5, 
                                            validate='key', textvariable=self.thresholdstring,
                                            validatecommand=(self.threshold_validation, '%P'))
        self.cde_threshold_entry.insert(0, '0.6')
        self.cde_dict_label = tk.Label(self.opts_lbframe, text = 'No CDE Dictionary File Selected',
                                         width = 30, bg='white')
        self.cde_dict_button = tk.Button(self.opts_lbframe, text='Select file',
                                         command=self.load_cde_dict_file)

        

    def __packing(self):
        self.opts_lbframe.pack(fill='both', ipadx=2, ipady=2)
        self.categories_label.grid(row=0, column=0, sticky='e')
        self.categories_entry.grid(row=0, column=1, sticky='w')
        self.sample_rows_label.grid(row=1, column=0, sticky='e')
        self.sample_rows_entry.grid(row=1, column=1, sticky='w')
        self.na_option_chbutton.grid(row=2, column=0, sticky='e')
        self.cde_dict_separator.grid(row=0, column=2, rowspan=3, padx= 4, sticky="ns")
        self.cde_dict_label2.grid(row=0, column=3, columnspan=2, pady=4, padx=4)
        self.cde_threshold_label.grid(row=1, column=3, pady=4, sticky='e')
        self.cde_threshold_entry.grid(row=1, column=4, sticky='w')        
        self.cde_dict_label.grid(row=2, column=3, pady=4, padx=4)
        self.cde_dict_button.grid(row=2, column=4)

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

def valid_threshold(s):
    if s == '':
        return True
    try:
        num = float(s)
        if num >= 0.0 and num <= 1.0:
            return True
        else:
            return False
    except ValueError:
        return False



