#!/usr/bin/env python3
import os
from pathlib import Path
import csv
from collections import namedtuple
from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from mipqctool.controller import InferSchema
from mipqctool.gui.metadataframe import MetadataFrame
from mipqctool.gui.guicorr import guiCorr
from mipqctool.gui.inferoptionsframe import InferOptionsFrame
from mipqctool.model.dcatalogue.node import Node
#from prepare import produce_encounter_properties, produce_patient_properties
#from prepare import produce_unpivot_files, produce_run_sh_script
from mipqctool.config import LOGGER

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
path = Path(DIR_PATH)
parentPath= path.parent

UnpivotCsv = namedtuple('UnpivotCsv', ['name', 'headers', 'selected', 'unpivoted'])

class MappingTab(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.corrs = []
        # holds a TableReport object for getting statistics for each dataset columns
        self.inferschema = None
        self.__loadTrFunctions()

        #self.__create_all_frames()
        #self.unpivotcsvs = {}
        #self.selected_csv_name = None #I it is not needed since it is stored in csv_file_label
        self.csv_file_path = None
        self.csv_file_headers = []#List of the CSV headers
        self.outputfolder = None
        #self.cde_file = None #Same here.
        self.cde_file_path = None
        self.cdes_d = {}#Dict of CDEs: key:code->value:DcVariable
        self.cdes_l = []#List of CDE codes: just to preserve the original sequence when they had been parsed in the JSON
        self.rootnode = None
        self.__init()
        self.__packing()

    def __init(self):
        # Hospital name frame
        self.hosp_labelframe = tk.LabelFrame(self, text='Hospital')
        self.hospital_label = tk.Label(self.hosp_labelframe, text='Hospital Code:')
        self.hospital_entry = tk.Entry(self.hosp_labelframe)

        # cde metadata frame
        self.cde_md_frame = MetadataFrame(self)
        self.cde_md_frame.tblabelframe.config(text='Target CDE metadata')

        # Infer frame
        self.infer_opt_frame = InferOptionsFrame(self)
        self.infer_opt_frame.opts_lbframe.config(text='Source csv infer options for CDE correspondance suggestion (Optional)')
        self.infer_opt_frame.cde_dict_label2.config(text='CDE correspondance suggestion (Optional)')

        # Mapping input csv file frame
        self.harm_labelframe = tk.LabelFrame(self, text='Mapping Configuration')
        # csv subframe
        self.csv_frame = tk.Frame(self.harm_labelframe)
        #self.harm_label_csv = tk.Label(self.csv_frame, text='CSV File:')
        self.csv_file_label = tk.Label(self.csv_frame, text='Source CSV file Not selected', bg='white', pady=4, width=40)
        self.csv_load_btn = tk.Button(self.csv_frame, text='Select', command=self.load_data_csv)
        self.suggest_btn = tk.Button(self.csv_frame, text='Suggest CDE correspondences', state='disabled')

        self.corr_label1 = tk.Label(self.harm_labelframe, text='Correspondances')
 
        # correspondances subframe
        self.corr_frame = tk.Frame(self.harm_labelframe)
        self.corr_scollbar = tk.Scrollbar(self.corr_frame)
        self.corr_listbox1 = tk.Listbox(self.corr_frame, yscrollcommand=self.corr_scollbar.set, width=35)
        self.corr_listbox2 = tk.Listbox(self.corr_frame, yscrollcommand=self.corr_scollbar.set)
        self.corr_btn_frame = tk.Frame(self.corr_frame)
        self.corr_add_btn = tk.Button(self.corr_frame, text='Add', width=10)
        self.corr_edit_bth = tk.Button(self.corr_frame, text='Edit', width=10)
        self.corr_remove_btn = tk.Button(self.corr_frame, text='Remove', width=10)

        self.map_save_btn = tk.Button(self.corr_frame, text='Save mapping', width=10, state='disabled')
        self.map_load_btn =tk.Button(self.corr_frame, text='Load mapping', width=10, state='disabled')


        #Output frame
        self.out_frame = tk.Frame(self.harm_labelframe)
        self.out_folder_lbl = tk.Label(self.out_frame, text='Output Folder Not Selected', bg='white', width=40)       
        self.out_folder_btn = tk.Button(self.out_frame, text='Open', command=self.select_output)
        
        self.exec_mapping_btn = tk.Button(self.out_frame, text= 'Run Mapping Task')
        


    def __packing(self):
        # Hospital name Frame
        #self.hosp_labelframe.pack()
        self.hospital_label.grid(row=0, column=0,sticky='w')
        self.hospital_entry.grid(row=0, column=1, columnspan=2, sticky='w')

        # metadata Frame
        self.cde_md_frame.pack(fill='both')

         # infer Option Frame
        self.infer_opt_frame.pack(fill='both', padx=4)
        self.infer_opt_frame.cde_dict_label2.grid_forget()
        self.infer_opt_frame.cde_threshold_label.grid_forget()
        self.infer_opt_frame.cde_threshold_entry.grid_forget()
        self.infer_opt_frame.cde_threshold_label.grid(row=0, column=3, pady=4, sticky='e')
        self.infer_opt_frame.cde_threshold_entry.grid(row=0, column=4, sticky='w')
        self.infer_opt_frame.cde_dict_label.grid_forget()
        self.infer_opt_frame.cde_dict_button.grid_forget()
        self.infer_opt_frame.cde_dict_label.grid(row=1, column=3, pady=4, padx=4)
        self.infer_opt_frame.cde_dict_button.grid(row=1, column=4)

        # Mapping Frame
        self.harm_labelframe.pack(fill='both', padx=4)
        # csv subframe
        self.csv_frame.pack(fill='y')
        #self.harm_label_csv.pack(side='left')
        self.csv_file_label.pack(side='left', padx=2)
        self.csv_load_btn.pack(side='left')
        self.suggest_btn.pack(side='left')
        
        self.corr_label1.pack()

        # correspondances subframe
        self.corr_frame.pack(fill='y')
        self.corr_listbox1.pack(side='left', fill='y', padx=2)
        self.corr_listbox2.pack(side='left', fill='y')
        self.corr_scollbar.pack(side='left', fill='y')
        self.corr_btn_frame.pack(side='left', padx=5, pady=4)
        self.corr_add_btn.pack()
        self.corr_edit_bth.pack()
        self.corr_remove_btn.pack()
        self.map_load_btn.pack(pady=(17, 1))
        self.map_save_btn.pack()

        # Output Frame
        self.out_frame.pack(fill='x', padx=4)
        self.out_folder_lbl.grid(row=0, column=1, pady=2)
        self.out_folder_btn.grid(row=0, column=2, padx=2)
        self.exec_mapping_btn.grid(row=0, column=3, sticky='e', padx=(75, 1))

    def __loadTrFunctions(self):
        #read the trFunctions.csv and load the trFunctions dict (NOT TrFunction instances..!)
        #This dict will be loaded in Combobox functions_cbox in guiCorr!!
        self.trFunctions = {}
        #with open(DIR_PATH+'/mapping/trFunctions.csv', 'r') as F:
        with open(os.path.join(str(parentPath) ,'data', 'trFunctions.csv'), 'r') as F:
            functionsFile = csv.DictReader(F)
            for row in functionsFile:
                self.trFunctions[row["label"]]=row["expression"]

    def add_items(self, headers, listbox):
        index = 1
        for header in headers:
            listbox.insert(index, header)
            index += 1

    def load_data_csv(self):
        filepath = tkfiledialog.askopenfilename(title='select patient csv file',
                                                filetypes=(('csv files', '*.csv'),
                                                           ('all files', '*.*')))
        if filepath:
            csv_name = os.path.basename(filepath)
            self.patientcsv = csv_name
            with open(filepath, 'r') as csvfile:
                data = csv.DictReader(csvfile)
                self.csv_file_headers = data.fieldnames
            self.csv_file_label.config(text=csv_name)
            self.csv_file_path = filepath
            self.inferschema = InferSchema.from_disc(filepath)
                #self.p_csv_headers_cbox.config(values=data.fieldnames)
            


   
    #Traverses the CDE-tree and stores the CDEs in self.cdes_d & l
    def store_cdes_first(self):
        self.store_cdes(current=self.rootnode)
    def store_cdes(self, current):
        if current:
            variables = current.variables
            for var in variables:
                self.cdes_l.append(var.label)
                self.cdes_d.update({var.label : var})#this is how u add a key-value pair to a Dictionary... Oh my...
            groups = current.children
            for child in groups:
                self.store_cdes(current=child)
        else: return
  
    def select_output(self):
        outputfolder = tkfiledialog.askdirectory(title='Select Output Folder')
        if outputfolder:
            if not os.path.isdir(outputfolder):
                os.mkdir(outputfolder)
            self.outputfolder = outputfolder
            self.out_folder_lbl.config(text=outputfolder)

 