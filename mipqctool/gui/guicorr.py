#!/usr/bin/env python3
import os
#from tkinter import *
#from tkinter.ttk import *
from tkinter import ttk
import tkinter as tk
import json

class guiCorr():
    """Whenever the New Button in prepro_guiNEW is pushed, a guiCorr object is created.
    :param button: The New Button in the prepro_guiNEW window
    :param c: The list of the correspondences in prepro_guiNEW
    :param i: The serial number of THIS correspondence in prepro_guiNEW
    :param trFunctions: The dictionnary with all the transformation Functions
    :param csv_columns: A list with the headers of the dataset CSV
    :param cdes_d: 
    :param cdes_l:"""
    def __init__(self, button, c, i, trFunctions, csv_columns, cdes_d, cdes_l):
        self.button = button
        self.corrs = c
        self.i_cor = i
        self.trFunctions = trFunctions #Dict: key:Label->Value:Expression
        self.csv_columns = csv_columns #List
        self.cdes_d = cdes_d #Dict: 
        self.cdes_l = cdes_l
        #self.newCorr = None
        self.button.configure(state="disable")
        self.master = tk.Tk()
        self.master.geometry("750x150")
        self.master.title("Mapping #"+str(i)+"#")
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.corr_win()

    def corr_win(self):
        self.harm_label_col = tk.Label(self.master, text='Column')
        self.harm_label_fun = tk.Label(self.master, text='Function')
        self.harm_label_exp = tk.Label(self.master, text='Expression')
        self.harm_label_cde = tk.Label(self.master, text='CDE')
        #
        self.columns_cbox = ttk.Combobox(self.master, values=self.csv_columns, width=20)
        self.functions_cbox = ttk.Combobox(self.master, values=sorted(list(self.trFunctions.keys())), width=20)
        self.expressions_text = tk.Text(self.master, width=40, height=6)
        #self.expressions_text.insert(tk.INSERT, "")#initilization
        self.harm_plusCol_btn = tk.Button(self.master, text='+', command=self.add_column)
        self.harm_plusFun_btn = tk.Button(self.master, text='+', command=self.add_function)
        self.cdes_cbox = ttk.Combobox(self.master, values=self.cdes_l, width=20)
        self.harm_save_btn = tk.Button(self.master, text='Save', command=self.save)#save correrspondence
        self.harm_cancel_btn = tk.Button(self.master, text='Cancel', command=self.cancel)#cancel correspondence
        #ok now start packing...
        #
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
        temp = temp + self.columns_cbox.get()
        self.expressions_text.insert(tk.END, temp)

    def add_function(self):
        temp = self.expressions_text.get(1.0, tk.END)
        self.expressions_text.delete(1.0, tk.END)
        #print('Add in Text Box: ', self.functions_cbox.get())
        temp = temp + self.trFunctions[self.functions_cbox.get()]
        self.expressions_text.insert(tk.END, temp)
    
    def save(self):
        expression = expressions_text.get("1.0", END)
        #call the MIPMAP py parser
        self.corrs.append(Correspondence(expression=expression))#self.corrs is a reference to the original prepro_guiNEW's corrs list
        self.button.configure(state="active")
        self.master.destroy()

    def cancel(self):
        self.button.configure(state="active")
        self.master.destroy()

    def on_close(self):
        self.button.configure(state="active")
        self.master.destroy()