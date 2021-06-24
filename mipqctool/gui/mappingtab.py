#!/usr/bin/env python3
import os
from pathlib import Path
import csv
import json
from threading import Thread

import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from mipqctool.controller import MipCDEMapper, CDEsController
#from mipqctool.controller.mipcdemapper import PARENTPATH
from mipqctool.gui.metadataframe import MetadataFrame
from mipqctool.gui.guicorr import guiCorr
from mipqctool.gui.inferoptionsframe import InferOptionsFrame
from mipqctool.config import LOGGER

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
PATH = Path(DIR_PATH)
PARENTPATH = PATH.parent


class MappingTab(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.cdemapper = None
        self.__loadtrfunctions()
        self.csv_file_path = None
        self.csv_file_headers = [] #List of the CSV headers
        self.csv_name = None
        self.cde_name = None # cde csv filename from cdecontroller

        self.outputfolder = None
        self.__init()
        self.__packing()

    def __init(self):

        # cde metadata frame
        self.cde_md_frame = MetadataFrame(self)
        self.cde_md_frame.tblabelframe.config(text='Target CDE metadata (Step 1)')

        # Infer frame
        self.infer_opt_frame = InferOptionsFrame(self)
        self.infer_opt_frame.opts_lbframe.config(text='Source csv infer options (Step 2)')
        self.infer_opt_frame.cde_dict_label2.config(text='CDE correspondence suggestion (Optional)')

        # Mapping input csv file frame
        self.harm_labelframe = tk.LabelFrame(self, text='Mapping Configuration (Step 3)')
        # csv subframe
        self.csv_frame = tk.Frame(self.harm_labelframe)
        #self.harm_label_csv = tk.Label(self.csv_frame, text='CSV File:')
        self.csv_file_label = tk.Label(self.csv_frame, text='Source CSV file Not selected', bg='white', pady=4, width=30)
        self.csv_load_btn = tk.Button(self.csv_frame, text='Select and Create', command=self.threaded_load_data_csv)
        self.suggest_btn = tk.Button(self.csv_frame, text='Suggest CDE correspondences',
                                     state='disabled', command=self.threaded_suggest_corrs)

        self.corr_label = tk.Label(self.harm_labelframe, text='Correspondences')

        # correspondances subframe
        self.corr_frame = tk.Frame(self.harm_labelframe)
        self.corr_scrollbar = tk.Scrollbar(self.corr_frame)
        self.corr_subframe1 = tk.Frame(self.corr_frame)
        self.corr_subframe2 = tk.Frame(self.corr_frame)
        self.corr_label1 = tk.Label(self.corr_subframe1, text='Source Columns')
        self.corr_label2 = tk.Label(self.corr_subframe2, text='CDE')
        self.corr_horiz_scrollbar1 = tk.Scrollbar(self.corr_subframe1, orient='horizontal')
        self.corr_horiz_scrollbar2 = tk.Scrollbar(self.corr_subframe2, orient='horizontal')
        self.corr_listbox1 = tk.Listbox(self.corr_subframe1,
                                        xscrollcommand=self.corr_horiz_scrollbar1.set,
                                        yscrollcommand=self.corr_scrollbar.set,
                                        width=35)
        self.corr_listbox1.bind('<<ListboxSelect>>', self.on_select_corr1)
        self.corr_listbox2 = tk.Listbox(self.corr_subframe2,
                                        xscrollcommand=self.corr_horiz_scrollbar2.set,
                                        yscrollcommand=self.corr_scrollbar.set)
        #self.corr_listbox2.bind('<<ListboxSelect>>', self.on_select_corr2)

        self.corr_horiz_scrollbar1.config(command=self.corr_listbox1.xview)
        self.corr_horiz_scrollbar2.config(command=self.corr_listbox2.xview)
        self.corr_scrollbar.config(command=self.yview)
        self.corr_btn_frame = tk.Frame(self.corr_frame)
        self.corr_add_btn = tk.Button(self.corr_frame, text='Add', width=10, command=self.add_corr, state='disabled')
        self.corr_edit_bth = tk.Button(self.corr_frame, text='Edit', width=10, command=self.edit_corr, state='disabled')
        self.corr_remove_btn = tk.Button(self.corr_frame, text='Remove', width=10, command=self.remove_corr, state='disabled')
        self.corr_mapped_label = tk.Label(self.corr_frame, text='CDEs mapped: 0')
        self.corr_not_mapped_label = tk.Label(self.corr_frame, text='CDEs not mapped: 0')


        #self.map_save_btn = tk.Button(self.corr_frame, text='Save mapping', width=10, state='disabled')
        #self.map_load_btn = tk.Button(self.corr_frame, text='Load mapping', width=10, state='disabled')


        #Output frame
        self.out_frame = tk.Frame(self.harm_labelframe)
        self.out_folder_lbl = tk.Label(self.out_frame, text='Output Folder Not Selected', bg='white', width=40)       
        self.out_folder_btn = tk.Button(self.out_frame, text='Open', command=self.select_output)
        self.save_xml_btn = tk.Button(self.out_frame, text='Save map.xml', command=self.savemapxml)
        
        self.exec_mapping_btn = tk.Button(self.out_frame, text= 'Run Mapping Task', command=self.threaded_run_mapping)

    def __packing(self):

        # metadata Frame
        self.cde_md_frame.pack(fill='both')

        # infer Option Frame
        self.infer_opt_frame.pack(fill='both', padx=4)
        # self.infer_opt_frame.cde_dict_label2.grid_forget()
        # self.infer_opt_frame.cde_threshold_label.grid_forget()
        # self.infer_opt_frame.cde_threshold_entry.grid_forget()
        # self.infer_opt_frame.cde_threshold_label.grid(row=0, column=3, pady=4, sticky='e')
        # self.infer_opt_frame.cde_threshold_entry.grid(row=0, column=4, sticky='w')
        # self.infer_opt_frame.cde_dict_label.grid_forget()
        # self.infer_opt_frame.cde_dict_button.grid_forget()
        # self.infer_opt_frame.cde_dict_label.grid(row=1, column=3, pady=4, padx=4)
        # self.infer_opt_frame.cde_dict_button.grid(row=1, column=4)

        # Mapping Frame
        self.harm_labelframe.pack(fill='both', padx=4)
        # csv subframe
        self.csv_frame.pack(fill='y')
        #self.harm_label_csv.pack(side='left')
        self.csv_file_label.pack(side='left', padx=2)
        self.csv_load_btn.pack(side='left')
        self.suggest_btn.pack(side='left')
        
        self.corr_label.pack()

        # correspondances subframe
        self.corr_frame.pack(fill='y')
        self.corr_subframe1.pack(side='left', fill='y', padx=2)
        self.corr_subframe2.pack(side='left', fill='y', padx=2)
        self.corr_scrollbar.pack(side='left', fill='y')
        
        self.corr_label1.pack()
        self.corr_listbox1.pack()
        self.corr_horiz_scrollbar1.pack(fill='x')
        
        self.corr_label2.pack()
        self.corr_listbox2.pack()
        self.corr_horiz_scrollbar2.pack(fill='x')

        self.corr_btn_frame.pack(side='left', padx=5, pady=4)
        self.corr_add_btn.pack()
        self.corr_edit_bth.pack()
        self.corr_remove_btn.pack()
        self.corr_mapped_label.pack(pady=(4,1))
        self.corr_not_mapped_label.pack()

        #self.map_load_btn.pack(pady=(17, 1))
        #self.map_save_btn.pack()

        # Output Frame
        self.out_frame.pack(fill='x', padx=4)
        self.out_folder_lbl.grid(row=0, column=1, pady=2)
        self.out_folder_btn.grid(row=0, column=2, padx=2)
        self.save_xml_btn.grid(row=0, column=3, padx=2)
        self.exec_mapping_btn.grid(row=0, column=4, sticky='e', padx=(15, 1))

    def add_items(self, headers, listbox):
        index = 1
        for header in headers:
            listbox.insert(index, header)
            index += 1

    def threaded_load_data_csv(self):
        t1 = Thread(target=self.load_data_csv)
        t1.start()
    
    def load_data_csv(self):
        self.csv_load_btn.config(state='disabled')
        warningtitle = 'Could create Mapping'
        filepath = tkfiledialog.askopenfilename(title='select source csv file',
                                                filetypes=(('csv files', '*.csv'),
                                                           ('all files', '*.*')))
        self.cde_md_frame.global_disable()
        if filepath:
            csv_name = os.path.basename(filepath)
            cdescontroller = self.__get_cdecontroller()
            if cdescontroller:
                na_empty_strings_only = self.infer_opt_frame.na_empty_strings_only.get()
                if self.infer_opt_frame.max_categories.get() == '':
                    maxlevels = 10
                else:
                    maxlevels = int(self.infer_opt_frame.max_categories.get())
                if self.infer_opt_frame.sample_rows.get() == '':
                    sample_rows = 100
                else:
                    sample_rows = int(self.infer_opt_frame.sample_rows.get())
                self.cdemapper = MipCDEMapper(filepath,
                                              cdescontroller=cdescontroller,
                                              sample_rows=sample_rows,
                                              maxlevels=maxlevels,
                                              na_empty_strings_only=na_empty_strings_only)

                self.csv_file_headers = self.cdemapper.source_headers
                self.csv_file_label.config(text=csv_name)
                self.csv_file_path = filepath
                self.csv_name = csv_name
                if self.infer_opt_frame.cde_dict:
                    self.suggest_btn.config(state='normal')
            self.corr_listbox1.delete(0, tk.END)
            self.corr_listbox2.delete(0, tk.END)
            self.corr_add_btn.config(state='normal')
            self.corr_edit_bth.config(state='normal')
            self.corr_remove_btn.config(state='normal')
        else:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select source csv file first!')
        

        self.csv_load_btn.config(state='normal')

    def threaded_suggest_corrs(self):
        t1 = Thread(target=self.suggest_corrs)
        t1.start()

    def suggest_corrs(self):
        self.suggest_btn.config(state='disabled')
        warningtitle = 'Could not make suggestions'
        if self.infer_opt_frame.cde_dict:
            if self.infer_opt_frame.thresholdstring.get() == '':
                threshold = 0.6
            else:
                threshold = float(self.infer_opt_frame.thresholdstring.get())
            
            self.cdemapper.suggest_corr(self.infer_opt_frame.cde_dict,
                                        threshold=threshold)
            LOGGER.info('Done with the correspondences suggestions..Updating listbox...')
            self.update_listbox_corr()
        else:
            tkmessagebox.showwarning(warningtitle,
                                     'Could not find the CDE dictionary file')
        self.suggest_btn.config(state='normal')

    def add_corr(self):
        cor_gui = guiCorr(self)

    def edit_corr(self):
        cde = self.corr_listbox2.get(self.corr_listbox2.curselection())
        cor_gui = guiCorr(self, cde)

    def remove_corr(self):
         selection = self.corr_listbox2.curselection()
         cde = self.corr_listbox2.get(selection)
         self.cdemapper.remove_corr(str(cde))
         self.update_listbox_corr()
  
    def select_output(self):
        outputfolder = tkfiledialog.askdirectory(title='Select Output Folder')
        if outputfolder:
            if not os.path.isdir(outputfolder):
                os.mkdir(outputfolder)
            self.outputfolder = outputfolder
            self.out_folder_lbl.config(text=outputfolder)

    def savemapxml(self):
        xmlfilepath = tkfiledialog.asksaveasfilename(
            filetypes=(
                ('xml files', '*.xml'), 
                ("All files", "*.*")
            )
        )
        if xmlfilepath:
            folder = os.path.dirname(xmlfilepath)
            cdefilepath = os.path.join(folder, self.cdemapper.cde_filename)
            self.cdemapper.cdecontroller.save_csv_headers_only(cdefilepath)
            self.cdemapper.save_mapping(xmlfilepath)

    def threaded_run_mapping(self):
        t1 = Thread(target=self.run_mapping)
        t1.start()

    def run_mapping(self):
        "TODO: ADD control if the fields are filled and are corrs in mapping"
        msg = "Mapping task error"
        self.exec_mapping_btn.config(state='disabled')
        if not self.cdemapper:
            tkmessagebox.showerror(msg, 'No source file selected!')
        if len(self.cdemapper.cde_mapped) == 0:
            tkmessagebox.showerror(msg, 'There are no correspondences to map.')
        if not self.outputfolder:
            tkmessagebox.showerror(msg, 'No output folder selected.')
        self.cdemapper.run_mapping(self.outputfolder)
        self.exec_mapping_btn.config(state='normal')

    def update_listbox_corr(self):
        self.__update_cde_labels()
        self.corr_listbox1.delete(0, tk.END)
        self.corr_listbox2.delete(0, tk.END)
        i = 1
        for cde, sources in self.cdemapper.corr_sources.items():
            self.corr_listbox1.insert(i, sources)
            self.corr_listbox2.insert(i, cde)
            i += 1

    def on_select_corr1(self, event):
        w = event.widget
        selection = w.curselection()
        if selection:
            index = selection[0]
            self.corr_listbox1.select_set(index)
            self.corr_listbox2.select_set(index)


    def on_select_corr2(self, event):
        w = event.widget
        selection = w.curselection()
        if selection:
            index = selection[0]
            self.corr_listbox1.select_set(index)
            self.corr_listbox2.select_set(index)


    def yview(self, *args):
        self.corr_listbox1.yview(*args)
        self.corr_listbox2.yview(*args)

    def onmousewheel(self, event):
        # self.corr_scrollbar.yview("scroll", event.delta,"units")
        # self.corr_listbox2.yview("scroll",event.delta,"units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"
    
    def __update_cde_labels(self):
        if self.cdemapper.cde_mapped:
            mapped_count = len(self.cdemapper.cde_mapped)
            cdemappedstr = 'CDEs mapped: {}'.format(mapped_count)
            self.corr_mapped_label.config(text=cdemappedstr)
        else:
            self.corr_mapped_label.config(text='CDEs mapped: 0')

        if self.cdemapper.cde_not_mapped:
            not_mapped_count = len(self.cdemapper.cde_not_mapped)
            cdenotmappedstr = 'CDEs not mapped: {}'.format(not_mapped_count)
            self.corr_not_mapped_label.config(text=cdenotmappedstr)
        else:
            self.corr_not_mapped_label.config(text='CDEs not mapped: 0')

    def __get_cdecontroller(self):
        warningtitle = 'Can not retrieve CDE metadata!'
        dict_schema = None
        schema_type = 'dc'
        pathology = None
        version = None
        if self.cde_md_frame.from_disk.get():
            if self.cde_md_frame.metafilepath:
                with open(self.cde_md_frame.metafilepath) as json_file:
                    dict_schema = json.load(json_file)
                if self.cde_md_frame.json_type.get() == 1:
                    schema_type = 'qc'
            else:
                tkmessagebox.showwarning(warningtitle,
                                        'Please, select cde metadata file first!')
        else:
            if self.cde_md_frame.dc_json:
                dict_schema = self.cde_md_frame.dc_json
                pathology = self.cde_md_frame.selected_pathology.get()
                version = self.cde_md_frame.selected_version.get()
            else:
                tkmessagebox.showwarning(warningtitle,
                                         'Please, select CDE pathology and version!')

        if dict_schema:
            return CDEsController(dict_schema, schema_type=schema_type,
                                  pathology=pathology, version=version)
        else:
            return None

    def __loadtrfunctions(self):
        #read the trFunctions.csv and load the trFunctions dict (NOT TrFunction instances..!)
        #This dict will be loaded in Combobox functions_cbox in guiCorr!!
        self.trFunctions = {}
        #with open(DIR_PATH+'/mapping/trFunctions.csv', 'r') as F:
        with open(os.path.join(str(PARENTPATH) ,'data', 'trFunctions.csv'), 'r') as F:
            functionsFile = csv.DictReader(F)
            for row in functionsFile:
                self.trFunctions[row["label"]]=row["expression"]