#!/usr/bin/env python3
import os
#from tkinter import *
#from tkinter.ttk import *
from tkinter import ttk
import tkinter as tk
import json
from mipqctool.model.mapping import Correspondence
from mipqctool.config import LOGGER
from mipqctool.controller import CorrespondenceParser as CP

class guiCorr():
    """Whenever the New Button in prepro_guiNEW is pushed, a guiCorr object is created.
    :param button: The New Button in the prepro_guiNEW window
    :param c: The list of the correspondences in prepro_guiNEW
    :param i: The serial number of THIS correspondence in prepro_guiNEW
    :param trFunctions: The dictionnary with all the transformation Functions
    :param csv_columns: A list with the headers of the dataset CSV
    :param cdes_d: 
    :param cdes_l:"""
    def __init__(self, parent):
        #if not cdes_d or not cdes_l:#if the CDE metadata has not been loaded...
        #    LOGGER.info("Need to load a CDEs metadata file before start defining mapping correspondences!")
        #    return
        self.parent = parent
        #self.corrs = c
        #self.i_cor = i
        self.selected_table = tk.StringVar()
        self.selected_column = tk.StringVar()
        self.trFunctions = parent.trFunctions #Dict: key:Label->Value:Expression
        #self.csv_columns = csv_columns #List
        #self.cdes_d = cdes_d #Dict: 
        #self.cdes_l = cdes_l
        self.functions = []
        self.sourceCols = []
        self.expression = None
        self.master = tk.Tk()
        self.master.geometry("750x150")
        self.master.title("Mapping #"+"#")
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.__init()
        self.__packing()
        
    def __init(self):
        self.main_frame = tk.Frame(master=self.master)
        self.harm_label_col = tk.Label(self.main_frame, text='Column')
        self.harm_label_fun = tk.Label(self.main_frame, text='Function')
        self.harm_label_exp = tk.Label(self.main_frame, text='Expression')
        self.harm_label_cde = tk.Label(self.main_frame, text='CDE')
        #
        #self.columns_cbox = ttk.Combobox(self.master, values=self.csv_columns, width=20)
        self.tables_cbox = ttk.Combobox(self.main_frame, textvariable=self.selected_table)
        self.tables_cbox.bind('<<ComboboxSelected>>', self.on_select_table)
        self.columns_cbox = ttk.Combobox(self.main_frame, values=['1','2'],
                                         textvariable=self.selected_column)

        self.functions_cbox = ttk.Combobox(self.main_frame, values=sorted(list(self.trFunctions.keys())), width=20)
        self.expressions_text = tk.Text(self.main_frame, width=40, height=6)
        #self.expressions_text.insert(tk.INSERT, "")#initialization
        self.harm_plusCol_btn = tk.Button(self.main_frame, text='+', command=self.add_column)
        self.harm_plusFun_btn = tk.Button(self.main_frame, text='+', command=self.add_function)
        self.cdes_cbox = ttk.Combobox(self.main_frame, values=['1'], width=20)
        self.harm_save_btn = tk.Button(self.main_frame, text='Save', command=self.save)#save correrspondence
        self.harm_cancel_btn = tk.Button(self.main_frame, text='Cancel', command=self.cancel)#cancel correspondence
        #ok now start packing...
    
    
    def __packing(self):
        self.main_frame.pack()
        self.harm_label_col.grid(row=2, column=0)
        self.columns_cbox.grid(row=3, column=0)
        self.harm_plusCol_btn.grid(row=3, column=4)
        self.harm_label_fun.grid(row=4, column=0)
        self.functions_cbox.grid(row=5, column=0)
        self.harm_plusFun_btn.grid(row=5, column=4)
        self.harm_label_exp.grid(row=2, column=6)
        self.expressions_text.grid(row=3, column=6, rowspan=6)
        self.harm_label_cde.grid(row=2, column=9)
        self.cdes_cbox.grid(row=3, column=9)
        self.harm_cancel_btn.grid(row=6, column=8)
        self.harm_save_btn.grid(row=6, column=9)
        #self.u_scrolbar1.pack(side='right', fill='y')
        #self.u_scrolbar2.pack(side='right', fill='y')
        #self.harm_subframe_fun.grid(row=4, column=2, sticky='w')
        #self.u_scrolbar3.pack(side='right', fill='y')
        #self.harm_subframe_exp.grid(row=2, column=6)

    def add_column(self):
        temp = self.expressions_text.get(1.0, tk.END)
        self.expressions_text.delete(1.0, tk.END)
        if self.tables_cbox.current() > -1 and self.columns_cbox.current() > -1:
            temp = temp + '.'.join(self.tables_cbox.get(), self.columns_cbox.get())
        else:
            LOGGER.warning("Table or header not selected.")
        self.expressions_text.insert(tk.END, temp)

    def add_function(self):
        temp = self.expressions_text.get(1.0, tk.END)
        self.expressions_text.delete(1.0, tk.END)
        #print('Add in Text Box: ', self.functions_cbox.get())
        temp = temp + self.trFunctions[self.functions_cbox.get()]
        self.expressions_text.insert(tk.END, temp)
    
    def save(self):
        #try:
        self.expression = self.expressions_text.get("1.0", "end-1c")
        """except NameError as nm:
            LOGGER.info("-Empty expression text. The value stays the same...")
            self.expression = None
            pass"""
        #call the correspondence parser..!
        self.sourceCols, self.functions = CP.separateSColumnsFunctions(self.expression, self.trFunctions)
        #gia ka8e column sto self.sourceCols pou synantatai sto self.expression, kane replace....
        self.corrs.append(Correspondence(corParser.sourceCols, self.cdes_cbox.get(), self.expression))#self.corrs is a reference to the original prepro_guiNEW's corrs list
        self.parent.newButton.configure(state="active")
        self.master.destroy()
        LOGGER.info('*** Just created Mapping Correspondence #%d for CDE:%s ***', self.i_cor, self.corrs[self.i_cor-1])

    def cancel(self):
        self.parent.newCButton.configure(state="active")
        self.master.destroy()

    def on_close(self):
        self.parent.deiconfy()
        self.master.destroy()

    def on_select_table(self):
        pass