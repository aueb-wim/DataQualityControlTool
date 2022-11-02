import json

import tkinter as tk
from tkinter import ttk

from sqlalchemy import Constraint


class CleanWindow():
    def __init__(self, parent):
        self.parent = parent
        self.master = tk.Tk()
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.title('Data Cleaning Suggestions')
        self.column_new_value = tk.StringVar()
        self.__init()
        self.__packing()

    def __init(self):
        self.big_frame = tk.Frame(master=self.master, padx=2, pady=2)
        self.main_frame = tk.Frame(self.big_frame, padx=2, pady=2)
        self.label1= tk.Label(self.main_frame, text='Select Column:')
        columns_with_corrections = [key  for key, columnreport in self.parent.reportcsv.columnreports.items() if len(columnreport.all_corrections) > 0]
        self.columns_cbox = ttk.Combobox(self.main_frame, width=35,                                    
                                         values=columns_with_corrections)
        self.columns_cbox.bind("<<ComboboxSelected>>", self.on_select_column)


        self.label2 = tk.Label(self.main_frame, text = 'Replacements')
        self.sugg_frame = tk.Frame(self.main_frame)
        self.sugg_scrollbar = tk.Scrollbar(self.sugg_frame)
        self.sugg_listbox = tk.Listbox(self.sugg_frame,
                                       selectmode=tk.SINGLE,
                                       yscrollcommand=self.sugg_scrollbar.set,
                                       width=35, height=10)
        self.sugg_scrollbar.config(command=self.sugg_listbox.yview)
        self.edit_frame = tk.LabelFrame(self.big_frame, text='Suggestion Edit')
        self.edit_new_label = tk.Label(self.edit_frame, text='New Replacement Value')
        self.edit_new_entry = tk.Entry(self.edit_frame, width=15, textvariable=self.column_new_value)
        self.edit_update_button = tk.Button(self.edit_frame, width=8, text='Update', command=self.update_suggestion)
        self.edit_delete_button = tk.Button(self.edit_frame, width=8, text='Delete', command=self.delete_suggestion)

        self.constraint_frame = tk.LabelFrame(self.big_frame, text='Column Constraints')
        self.constraint_label = tk.Label(self.constraint_frame, background='white', width=25, height=15,
                                         justify=tk.LEFT)


    def __packing(self):
        self.big_frame.pack()

        self.constraint_frame.pack(side='left', fill='both')
        self.constraint_label.pack(anchor ='nw')

        self.main_frame.pack(side='left')
        self.label1.pack()
        self.columns_cbox.pack(padx=4, pady=4)
        self.label2.pack()
        self.sugg_frame.pack(fill='both', padx=4, pady=4)
        self.sugg_listbox.pack(side='left', fill='both')
        self.sugg_scrollbar.pack(side='left', fill=tk.Y)

        self.edit_frame.pack(side='left', fill='both')
        self.edit_new_label.pack()
        self.edit_new_entry.pack()
        self.edit_update_button.pack()
        self.edit_delete_button.pack()

        

    def on_select_column(self, event):
        if self.columns_cbox.current() > -1:
            sel_col = self.columns_cbox.get()
            self.__update_col_sugg(sel_col)

    def update_suggestion(self):
        column = self.columns_cbox.get()
        new_value = self.edit_new_entry.get()
        columnreport = self.parent.reportcsv.columnreports.get(column)
        suggestion_str = self.sugg_listbox.get(self.sugg_listbox.curselection())
        original_value = suggestion_str.split(' -> ')[0]
        columnreport.update_correction(original_value, new_value)
        self.parent.reportcsv.columnreports[column] = columnreport
        self.__update_col_sugg(column)
        self.edit_new_entry.delete(0, tk.END)


    def delete_suggestion(self):
        column = self.columns_cbox.get()
        columnreport = self.parent.reportcsv.columnreports.get(column)
        suggestion_str = self.sugg_listbox.get(self.sugg_listbox.curselection())
        original_value = suggestion_str.split(' -> ')[0]
        columnreport.delete_correction(original_value)
        self.parent.reportcsv.columnreports[column] = columnreport
        self.__update_col_sugg(column)
        self.edit_new_entry.delete(0, tk.END)
            

    def on_close(self):
        self.master.destroy()


    def __update_col_sugg(self, column):
        columnreport = self.parent.reportcsv.columnreports.get(column)
        self.sugg_listbox.delete(0,tk.END)
        all_corr = columnreport.all_corrections
        for item in all_corr:
            self.sugg_listbox.insert(all_corr.index(item), item)
        constraint_text = ''
        for con_type, constraint in columnreport.qcfield.constraints.items():
            if con_type == 'enum':
                ctext = 'enum: \n'
                for enum in constraint:
                    ctext += '\t* {}\n'.format(enum)
            else:
                ctext = '{} : {}\n'.format(con_type, constraint)
            constraint_text += ctext

        self.constraint_label.config(text=constraint_text)





