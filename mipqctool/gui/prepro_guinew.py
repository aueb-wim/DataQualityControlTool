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
from mipqctool.model.dcatalogue.node import Node
#from prepare import produce_encounter_properties, produce_patient_properties
#from prepare import produce_unpivot_files, produce_run_sh_script
from mipqctool.config import LOGGER

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
path = Path(DIR_PATH)
parentPath= path.parent

UnpivotCsv = namedtuple('UnpivotCsv', ['name', 'headers', 'selected', 'unpivoted'])

class Preprocess(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.corrs = []
        # holds a TableReport object for getting statistics for each dataset columns
        self.inferschema = None
        self.__loadTrFunctions()
        self.__create_all_frames()
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

    def __create_all_frames(self):
        self.__hospital_frame()
        self.__cdes_metadata_frame()
        self.__csv_file_frame()
        self.__output_frame()

    def __csv_file_frame(self):
        self.harm_labelframe = tk.LabelFrame(self, text='Mapping Configuration')
        self.harm_label_csv = tk.Label(self.harm_labelframe, text='CSV File:')
        self.csv_file_label = tk.Label(self.harm_labelframe, text='Not selected', bg='white', pady=4, width=40)
        self.csv_load_btn = tk.Button(self.harm_labelframe, text='Select', command=self.load_data_csv)
        self.separator = ttk.Separator(self.harm_labelframe, orient=tk.HORIZONTAL)
        #packing
        self.harm_labelframe.grid(row=2, columnspan=8, padx=4, pady=4, ipadx=4, ipady=4, sticky=['w','e'])
        self.harm_label_csv.grid(row=0, column=0)
        self.csv_file_label.grid(row=0, column=2)
        self.csv_load_btn.grid(row=0, column=4)
        self.separator.grid(row=1, columnspan=8)
        #now here comes the repeatable section with the correspondences
        for c in self.corrs:
            self.__corr_line(c)
        self.__corr_line()
        
    def __corr_line(self, c=None):
        if c is None:#all parameters in python are passed by reference
            self.newCButton = tk.Button(self.harm_labelframe, text="New",
                                        command=lambda: guiCorr(self,
                                                                c=self.corrs, 
                                                                i=len(self.corrs)+1,
                                                                trFunctions=self.trFunctions,
                                                                csv_columns=self.csv_file_headers,
                                                                cdes_d=self.cde_md_frame.cdescontroller.cdes_d, cdes_l=self.cde_md_frame.cdescontroller.cdes_l))
            self.newCButton.grid(row=len(self.corrs)+1, column=5)
            return
        self.label_corr = tk.Label(self.harm_labelframe, text="Mapping #"+self.corrs.index(c)+"# to "+c.target)
        self.editCButton = tk.Button(self.harm_labelframe, text="Edit")
        #packing
        self.label_corr.grid(row=i+1, column=0)
        self.editCButton.grid(row=i+1, column=5)

    def __hospital_frame(self):
        self.hosp_labelframe = tk.LabelFrame(self, text='Hospital')
        self.hospital_label = tk.Label(self.hosp_labelframe, text='Hospital Code:')
        self.hospital_entry = tk.Entry(self.hosp_labelframe)
        #packing...
        self.hosp_labelframe.grid(row=0, columnspan=8, padx=4, pady=4, ipadx=4, ipady=4, sticky=['w','e'])
        self.hospital_label.grid(row=0, column=0,sticky='w')
        self.hospital_entry.grid(row=0, column=1, columnspan=2, sticky='w')

    def __cdes_metadata_frame(self):
        # self.cde_labelframe = tk.LabelFrame(self, text='CDEs')
        # self.cde_label_file = tk.Label(self.cde_labelframe, text='Metadata file:')
        # self.cde_label = tk.Label(self.cde_labelframe, text='Not Selected', bg='white',  width=40)
        # self.cde_load_btn = tk.Button(self.cde_labelframe, text='Select', command=self.loadCDEs)
        # #packing...
        # self.cde_labelframe.grid(row=1, columnspan=8, padx=4, pady=4, ipadx=4, ipady=4, sticky=['w','e'])
        # self.cde_label_file.grid(row=0, column=0)
        # self.cde_label.grid(row=0, column=1, columnspan=3, padx=4, pady=4)
        # self.cde_load_btn.grid(row=0, column=5)
        self.cde_md_frame = MetadataFrame(self)
        self.cde_md_frame.grid(row=1, columnspan=8, padx=4, pady=4, ipadx=4, ipady=4, sticky=['w','e'])

    
    def __output_frame(self):
        self.out_labelframe = tk.LabelFrame(self, text='Output folder')
        self.out_label = tk.Label(self.out_labelframe, text='Not Selected', bg='white', width=40)       
        self.o_button1 = tk.Button(self.out_labelframe, text='Open', command=self.select_output)
        #self.o_button2 = tk.Button(self.out_labelframe, text='Create files', command=self.createfiles)
        #packing...
        self.out_labelframe.grid(row=7, columnspan=8, padx=4, pady=4, ipadx=4, ipady=4, sticky=['w','e'])
        self.out_label.grid(row=7, column=1, pady=2)
        self.o_button1.grid(row=7, column=2)
        #self.o_button2.grid(row=7, column=3, pady=2, padx=2)

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
            self.o_label2.config(text=outputfolder)
"""
    def createfiles(self):
        hospital_code = self.hospital_entry.get()
        warningtitle='Could not create config files'

        p_patientid = self.p_csv_headers_cbox.get()

        visitid = self.c_csv_headers_cbox1.get()
        c_patienid = self.c_csv_headers_cbox2.get()

        if hospital_code == '':
            tkmessagebox.showwarning(warningtitle,
                                     'Please, enter hospital code')
        
        elif not self.patientcsv:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select patient csv file')

        elif not p_patientid:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select patientID column in patient csv')

        elif not self.visitscsv:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select visits csv file')

        elif not visitid:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select visitID column in visits csv')

        elif not c_patienid:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select patientID column in visits csv')

        elif not self.outputfolder:
            tkmessagebox.showwarning(warningtitle,
                                     'Please, select configuration files output folder')

        produce_patient_properties(self.outputfolder, self.patientcsv, p_patientid, hospital_code)
        produce_encounter_properties(self.outputfolder, self.visitscsv, visitid, c_patienid, hospital_code)
        produce_run_sh_script(self.outputfolder, self.unpivotcsvs)
        if len(self.unpivotcsvs) != 0:
            for key, item in self.unpivotcsvs.items():
                produce_unpivot_files(self.outputfolder, item.name, item.selected, item.unpivoted)

        tkmessagebox.showinfo(title='Status info',
                message='Config files have been created successully')
"""
        
        
def main(): #(Outside class Application)
    """Main Application Window"""
    root = tk.Tk()
    app = Application(master=root)
    app.master.title('MIPMAP Mappings Configuration')
    app.master.resizable(False, False)
    #app.master.iconbitmap(os.getcwd() + '/images/mipmap.xbm')#needs .ico (or xbm?) file
    app.mainloop()


if __name__ == '__main__':
    main()
 