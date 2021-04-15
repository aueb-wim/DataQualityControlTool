#!/usr/bin/env python3
import os
#from tkinter import *
#from tkinter.ttk import *
from tkinter import ttk
import tkinter as tk
import tkinter.messagebox as tkmessagebox

from mipqctool.model.mapping import Correspondence
from mipqctool.model.mapping.functions import ifstr, Replacement
from mipqctool.config import LOGGER
from mipqctool.controller import CorrespondenceParser as CP
from mipqctool.exceptions import ExpressionError

class guiCorr():
    """Whenever the New Button in prepro_guiNEW is pushed, a guiCorr object is created.
    :A
    """
    def __init__(self, parent, cde=None):
        # the parent mappingtab object
        self.parent = parent
        self.trFunctions = parent.trFunctions #Dict: key:Label->Value:Expression
        self.expression = None
        self.selected_column = None
        self.selected_column_miptype = None
        self.selected_cde = None
        self.selected_cde_miptype = None

        # create GUI main window
        self.master = tk.Tk()
        #self.master.geometry("750x150")
        self.target_cde = cde

        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.parent.corr_add_btn.configure(state='disabled')
        self.parent.corr_edit_bth.configure(state='disabled')
        self.parent.corr_remove_btn.configure(state='disabled')
        self.__init()
        self.__packing()

        if self.target_cde:
            self.master.title("Editing Mapping for '{}' CDE".format(cde))
            self.__update_cde_info(self.target_cde)
            self.cdes_cbox.configure(state='disabled')
            expr = self.parent.cdemapper.get_corr_expression(self.target_cde)
            self.expressions_text.insert(tk.END, expr)
        else:
            self.master.title("New Mapping")
          
        
    def __init(self):
        self.main_frame = tk.Frame(master=self.master, padx=2, pady=2)
        
        #the left side  
        self.harm_frame = tk.Frame(self.main_frame)

        # cde frame
        self.cde_frame = tk.LabelFrame(self.harm_frame, text = 'CDE')
        #self.cde_label = tk.Label(self.cde_frame, text='CDE')
        self.cdes_cbox = ttk.Combobox(self.cde_frame, width=35, values=self.parent.cdemapper.cde_not_mapped)
        self.cdes_cbox.bind("<<ComboboxSelected>>", self.on_select_cde)
        self.cde_info_frame = tk.Frame(self.cde_frame)
        self.cde_info_scrollbar = tk.Scrollbar(self.cde_info_frame)
        self.cde_info_listbox = tk.Listbox(self.cde_info_frame,
                                           yscrollcommand=self.cde_info_scrollbar.set,
                                           width=30, height=5)
        self.cde_info_scrollbar.config(command=self.cde_info_listbox.yview)
        

        # source column frame
        self.src_frame = tk.LabelFrame(self.harm_frame, text = 'Source Columns')
        self.src_col_label = tk.Label(self.src_frame, text='Source Column')
        self.columns_cbox = ttk.Combobox(self.src_frame, values=self.parent.csv_file_headers,
                                         width=30)
        self.columns_cbox.bind("<<ComboboxSelected>>", self.on_select_column)
        self.col_plus_btn = tk.Button(self.src_frame, text='+', command=self.add_column)
        self.col_info_frame = tk.Frame(self.src_frame)
        self.col_info_scrollbar = tk.Scrollbar(self.col_info_frame)
        self.col_info_listbox = tk.Listbox(self.col_info_frame,
                                           yscrollcommand=self.col_info_scrollbar.set,
                                           width=30, height=5)
        self.col_info_scrollbar.config(command=self.col_info_listbox.yview)


        # function frame
        self.func_main_frame = tk.LabelFrame(self.main_frame, text='Functions')

        self.func_frame = tk.Frame(self.func_main_frame)
        self.func_label = tk.Label(self.func_frame, text='Mipmap Function')
        self.functions_cbox = ttk.Combobox(self.func_frame, values=sorted(list(self.trFunctions.keys())), width=20)
        self.func_plus_btn = tk.Button(self.func_frame, text='+', command=self.add_function)

        self.func_seperator = ttk.Separator(self.func_main_frame, orient='horizontal')
        
        self.func_replace_frame = tk.Frame(self.func_main_frame)        
        self.func_replace_label = tk.Label(self.func_replace_frame, text='Category Replacement Function')
        
        self.func_replace_src_frame = tk.Frame(self.func_replace_frame)
        self.func_replace_src_scrollbar_y = tk.Scrollbar(self.func_replace_src_frame)
        self.func_replace_src_scrollbar_x = tk.Scrollbar(self.func_replace_src_frame, orient='horizontal')
        self.func_replace_src_listbox = tk.Listbox(self.func_replace_src_frame,
                                                   yscrollcommand=self.func_replace_src_scrollbar_y.set,
                                                   xscrollcommand=self.func_replace_src_scrollbar_x.set,
                                                   width=15)
        self.func_replace_src_scrollbar_x.config(command=self.func_replace_src_listbox.xview)
        self.func_replace_src_scrollbar_y.config(command=self.func_replace_src_listbox.yview)
        
        self.func_replace_btn_frame = tk.Frame(self.func_replace_frame)
        self.func_replace_with_label = tk.Label(self.func_replace_btn_frame, text='Replace with:')
        self.func_replace_entry = tk.Entry(self.func_replace_btn_frame, width=10)
        self.func_replace_add_btn = tk.Button(self.func_replace_btn_frame, text='->', command=self.add_replacement)
        self.func_replace_rem_btn = tk.Button(self.func_replace_btn_frame, text='<-', command=self.del_replacement)

        self.func_replace_trg_frame = tk.Frame(self.func_replace_frame)
        self.func_replace_trg_scrollbar_y = tk.Scrollbar(self.func_replace_trg_frame)
        self.func_replace_trg_scrollbar_x = tk.Scrollbar(self.func_replace_trg_frame, orient='horizontal')
        self.func_replace_trg_listbox = tk.Listbox(self.func_replace_trg_frame,
                                                   yscrollcommand=self.func_replace_trg_scrollbar_y.set,
                                                   xscrollcommand=self.func_replace_trg_scrollbar_x.set,
                                                   width=15)
        self.func_replace_trg_scrollbar_x.config(command=self.func_replace_trg_listbox.xview)
        self.func_replace_trg_scrollbar_y.config(command=self.func_replace_trg_listbox.yview)

        self.func_rep_buttons_frame = tk.Frame(self.func_replace_frame)
        self.func_add_btn = tk.Button(self.func_rep_buttons_frame, text='+', command=self.add_replacement_expr)
        
        # the right side for holding the expression textbox and the cancel save buttons
        self.expr_frame = tk.Frame(self.main_frame)
        self.exp_label = tk.Label(self.expr_frame, text='Expression')
        self.expressions_text = tk.Text(self.expr_frame) #width=50, height=10)
        
        # buttons frame
        self.btn_frame = tk.Frame(self.expr_frame)
        self.harm_clear_btn = tk.Button(self.btn_frame, text='Clear') # clears the expression box
        self.harm_cancel_btn = tk.Button(self.btn_frame, text='Cancel', command=self.cancel)#cancel correspondence
        self.harm_save_btn = tk.Button(self.btn_frame, text='Save', command=self.save)#save correrspondence

    
    def __packing(self):
        self.main_frame.pack()

        # pack the bottom side
        self.expr_frame.pack(side='bottom', fill='both')
        self.exp_label.pack()
        self.expressions_text.pack(fill='both', padx=2, pady=2)
        self.btn_frame.pack(fill=tk.X)
        self.harm_save_btn.pack(side='right')
        self.harm_cancel_btn.pack(side='right')
        self.harm_clear_btn.pack(side='right', padx=(2,4))

        # pack left side first
        self.harm_frame.pack(side='left', fill='both')
        
        self.cde_frame.pack(fill='both', padx=4, pady=4)
        #self.cde_label.grid(row=0, column=0)
        self.cdes_cbox.pack(padx=2, pady=(2,5))
        self.cde_info_frame.pack(fill='both')
        self.cde_info_listbox.pack(side='left', padx=(2,0), pady=2)
        self.cde_info_scrollbar.pack(side='left', fill=tk.Y, padx=(0,2), pady=2)

        self.src_frame.pack(fill='both', padx=4, pady=4)
        self.src_col_label.grid(row=0, column=0, padx=2, pady=2)
        self.columns_cbox.grid(row=1, column=0, sticky=tk.W, padx=2, pady=(2, 5))
        self.col_plus_btn.grid(row=1, column=1, padx=2)
        self.col_info_frame.grid(row=2, column=0)
        self.col_info_listbox.pack(side='left')
        self.col_info_scrollbar.pack(side='left', fill=tk.Y)

        self.func_main_frame.pack(fill='both')

        self.func_frame.pack(fill='both', padx=2, pady=2)
        self.func_label.pack(side='top', padx=2, pady=2)
        self.functions_cbox.pack(side='left',padx=2, pady=(2, 5))
        self.func_plus_btn.pack(side='right', padx=2, pady=2)

        self.func_seperator.pack(fill='x')

        self.func_replace_frame.pack()
        self.func_replace_label.pack()

        self.func_replace_src_frame.pack(side='left')
        self.func_replace_src_scrollbar_x.pack(side='bottom', fill='x')
        self.func_replace_src_scrollbar_y.pack(side='right', fill='y')
        self.func_replace_src_listbox.pack(side='left')
        
        self.func_replace_btn_frame.pack(side='left')
        self.func_replace_with_label.pack()
        self.func_replace_entry.pack()
        self.func_replace_add_btn.pack()
        self.func_replace_rem_btn.pack()

        self.func_replace_trg_frame.pack(side='left')
        self.func_replace_trg_scrollbar_x.pack(side='bottom', fill='x')
        self.func_replace_trg_scrollbar_y.pack(side='right', fill='y')
        self.func_replace_trg_listbox.pack(side='left')
        
        self.func_rep_buttons_frame.pack(side='right')
        self.func_add_btn.pack(padx=2)
        
    def add_replacement(self):
        targetvalue = self.func_replace_entry.get()
        sourcevalue = self.func_replace_src_listbox.get(self.func_replace_src_listbox.curselection())
        LOGGER.debug('Target value is: {} and the source value is: {}'.format(targetvalue, sourcevalue))
        if targetvalue != '' and sourcevalue:
            stringforbox = '->'.join([sourcevalue, targetvalue])
            self.func_replace_trg_listbox.insert(tk.END, stringforbox)
        else:
            pass

    def del_replacement(self):
        self.func_replace_trg_listbox.delete(self.func_replace_trg_listbox.curselection())

    def add_replacement_expr(self):
        reps = self.func_replace_trg_listbox.get(0, tk.END)
        replacemnts = []
        source_col = self.parent.csv_name.replace(".csv","")+ '.' + self.selected_column
        LOGGER.debug('the repleacements are: {}'.format(reps))
        if len(reps) > 0:
            self.expressions_text.delete("1.0", "end-1c")
            for rep in reps:
                s = rep.split('->')
                replacemnts.append(Replacement(s[0], s[1]))
            expr = ifstr(source_col, replacemnts)
            LOGGER.info('the expression is: {}'.format(expr))
            self.expressions_text.insert('1.0', expr)


    def add_column(self):
        temp = ''
        if self.columns_cbox.current() > -1:
            temp = self.parent.csv_name.replace(".csv","")+ '.' + self.columns_cbox.get()
        else:
            LOGGER.warning("Table or header not selected.")
        self.expressions_text.insert(tk.INSERT, temp)

    def add_function(self):
        temp = ''
        #print('Add in Text Box: ', self.functions_cbox.get())
        temp = self.trFunctions[self.functions_cbox.get()]
        self.expressions_text.insert(tk.INSERT, temp)
    
    def save(self):
        #try:
        self.expression = self.expressions_text.get("1.0", "end-1c")

        if len(self.expression) == 0:
            tkmessagebox.showwarning('Mapping Warning',
                                     'Please, enter a valid expression!')
        else:
            try:
                # check the expression
                columnsused = CP.extractSColumnsFunctions(self.expression, self.trFunctions, self.parent.csv_file_headers)
                # are we editing and existing correspondence? 
                if self.target_cde:
                    self.parent.cdemapper.update_corr(self.target_cde, columnsused, self.expression)
                # if not create new 
                else:
                    if self.cdes_cbox.current() > -1:
                        self.parent.cdemapper.add_corr(self.cdes_cbox.get(), columnsused, self.expression)
                        self.parent.update_listbox_corr()
                        self.on_close()
                    else:
                        tkmessagebox.showwarning('Mapping Warning',
                                                'Please, select target CDE!')
                
            except ExpressionError as e:
                tkmessagebox.showwarning('Mapping Warning', str(e))

    def cancel(self):
        self.parent.corr_add_btn.configure(state="active")
        self.parent.corr_edit_bth.configure(state="active")
        self.parent.corr_remove_btn.configure(state="active")
        self.master.destroy()

    def on_close(self):
        self.parent.corr_add_btn.configure(state="active")
        self.parent.corr_edit_bth.configure(state="active")
        self.parent.corr_remove_btn.configure(state="active")
        self.master.destroy()

    def on_select_column(self, event):
        self.col_info_listbox.delete(0, tk.END)
        self.func_replace_src_listbox.delete(0, tk.END)
        self.selected_cde_miptype = None
        self.selected_column = None
        if self.columns_cbox.current() > -1:
            info = []
            sel_col = self.columns_cbox.get()
            col_stats = self.parent.cdemapper.get_col_stats(sel_col)
            dtype = col_stats['miptype']
            value_range = col_stats['value_range']
            info.append('Data type: ' + dtype)
            if dtype in ['numerical', 'integer'] :
                info.append('Min:' + str(value_range[0]))
                info.append('Max:' + str(value_range[1]))
            elif dtype == 'nominal':
                info.append('Categories:')
                categories = []
                for cat in value_range:
                    info.append(str(cat))
                    categories.append(str(cat))
                for item in categories:
                    self.func_replace_src_listbox.insert(categories.index(item), item)
            for item in info:
                self.col_info_listbox.insert(info.index(item), item)
            self.selected_cde_miptype = dtype
            self.selected_column = sel_col

    def on_select_cde(self, event):        
        if self.cdes_cbox.current() > -1:
            sel_cde = self.cdes_cbox.get()
            self.__update_cde_info(sel_cde)


    def __update_cde_info(self, cdecode, is_raw_header=False):
        self.cde_info_listbox.delete(0, tk.END)
        self.selected_cde_miptype = None
        info = []
        if is_raw_header:
            cdename = self.parent.cdemapper.get_cde_mipmap_header(cdecode)
        else:
            cdename = cdecode
        cde_info = self.parent.cdemapper.get_cde_info(cdename)
        dtype = cde_info['miptype']
        constraints = cde_info['constraints']
        info.append('Data type: ' + dtype)
        if dtype == 'nominal' and constraints:
            info.append('Categories:')
            for cat in constraints:
                info.append(str(cat))
        elif dtype in ['numerical', 'integer'] and constraints:
            info.append('min: ' + constraints[0])
            info.append('max: ' + constraints[1])
        else:
            info.append('No Constraints found')
        for item in info:
            self.cde_info_listbox.insert(info.index(item), item)
        self.selected_cde_miptype=dtype



