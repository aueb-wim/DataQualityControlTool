import os
import requests
import json

from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from mipqctool.controller import DcConnector
from mipqctool.model.qcfrictionless import QcSchema, QcTable, FrictionlessFromDC
from mipqctool.config import LOGGER, DC_DOMAIN, DC_SUBDOMAIN_ALLPATHOLOGIES


class MetadataFrame(tk.Frame):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Metadata from disk vars
        self.metafilepath = None
        self.from_disk = tk.BooleanVar()
        self.from_disk.set(True)
        # set default option for json metadata type to Frictionless
        self.json_type = tk.IntVar()
        self.json_type.set(1)
        self.json_types = [('Frictionless', 1), ('DataCatalogue', 2)]
        # DataCatalogue related vars
        self.from_dc = tk.BooleanVar()
        self.from_dc.set(False)
        self.selected_pathology = tk.StringVar()
        self.selected_version = tk.StringVar()
        self.dc_json = None

        self.__init()
        self.__packing()
        self._disable(self.dc_frame)

    def __init(self):
        # Metadata main labeled frame
        self.tblabelframe = tk.LabelFrame(self, text='Metadata - Dataset\'s Schema')
        self.seperator = ttk.Separator(self.tblabelframe,
                                       orient=tk.HORIZONTAL)

        # metadata from local disc frame
        self.lc_frame = tk.Frame(self.tblabelframe)
        self.fromdisc_cbutton = tk.Checkbutton(self.tblabelframe,
                                               text='From Local Disk',
                                               variable=self.from_disk,
                                               command=self._check_lc)
        self.metaname_label = tk.Label(self.lc_frame, text='Not selected',
                                       bg='white', pady=4, width=46)
        self.setfilepath()#call this so as to initialize a couple of objects...
        self.metaload_button = tk.Button(self.lc_frame, text='Select File',
                                         command=self.setmetadatafile)

        self.json_tblabelframe = tk.LabelFrame(self.lc_frame,
                                               text='Json Type:')
        self.json_radiobutton1 = tk.Radiobutton(self.json_tblabelframe,
                                                text='Frictionless',
                                                padx=4,
                                                variable=self.json_type,
                                                value=1)
        self.json_radiobutton2 = tk.Radiobutton(self.json_tblabelframe,
                                                text='DataCatalogue',
                                                padx=4,
                                                variable=self.json_type,
                                                value=2)

        # DataCatalogue Frame
        self.fromdc_cbutton = tk.Checkbutton(self.tblabelframe,
                                             text='From DataCataloge',
                                             variable=self.from_dc,
                                             command=self._check_dc)

        self.dc_frame = tk.Frame(self.tblabelframe)

        self.dc_label1 = tk.Label(self.dc_frame, text='Select Pathology:')
        self.dc_label2 = tk.Label(self.dc_frame, text='Select CDE version:')

        self.dc_combox1 = ttk.Combobox(self.dc_frame,
                                       textvariable=self.selected_pathology)
        self.dc_combox1.bind('<<ComboboxSelected>>', self.on_select_pathology)
        self.dc_combox2 = ttk.Combobox(self.dc_frame,
                                       textvariable=self.selected_version)
        self.dc_combox2.bind('<<ComboboxSelected>>', self.on_select_version)

        self.dc_label3 = tk.Label(self.dc_frame, text='--- (Optional) ---')

        self.dc_cde_button = tk.Button(self.dc_frame, text='Get pathologies',
                                       command=self.get_all_cdes)

        self.dc_save_button = tk.Button(self.dc_frame, text='Save to disc',
                                        command=self.save_2_disc)

    def __packing(self):
        # metadata frame packing
        # Main Skeleton
        self.tblabelframe.pack(fill='both', expand='yes', ipadx=2, ipady=4,
                               padx=4, pady=4)
        self.fromdisc_cbutton.pack(anchor='w', padx=2, pady=2)
        self.lc_frame.pack(fill='x', expand='yes', padx=4, pady=4)  
        self.seperator.pack(fill='x', pady=4)
        self.fromdc_cbutton.pack(anchor='w', padx=2, pady=2)
        self.dc_frame.pack()

        # from local file frame

        self.json_tblabelframe.pack(side='left', anchor='w', padx=2)
        self.json_radiobutton1.pack(anchor='w')
        self.json_radiobutton2.pack(anchor='w')
        self.metaname_label.pack(side='left', anchor='w', padx=2)
        self.metaload_button.pack(side='left', anchor='e', padx=2)

        # From Data Catalogue Frame
        self.dc_frame.pack(fill='x', expand='yes')
        self.dc_label1.grid(row=0, column=0)
        self.dc_label2.grid(row=0, column=1)
        self.dc_cde_button.grid(row=0, column=3)
        self.dc_combox1.grid(row=1, column=0, padx=2)
        self.dc_combox2.grid(row=1, column=1, padx=2)
        self.dc_label3.grid(row=1, column=2, padx=2)
        self.dc_save_button.grid(row=1, column=3, pady=4, sticky='e')

    def _check_dc(self):
        if self.from_dc.get():
            self.from_disk.set(False)
            self._disable(self.lc_frame)
            self._enable(self.dc_frame)
        else:
            self.from_disk.set(True)
            self._check_lc()

    def _check_lc(self):
        if self.from_disk.get():
            self.from_dc.set(False)
            self._disable(self.dc_frame)
            self._enable(self.lc_frame)
        else:
            self.from_dc.set(True)
            self._check_dc()

    def _disable(self, frame):
        for child in frame.winfo_children():
            try:
                child.config(state='disabled')
            except tk.TclError:
                self._disable(child)

    def _enable(self, frame):
        for child in frame.winfo_children():
            try:
                child.config(state='normal')
            except tk.TclError:
                self._enable(child)

    def global_disable(self):
        for child in self.winfo_children():
            try:
                child.config(state='disabled')
            except tk.TclError:
                self._enable(child)

    def global_enable(self):
        for child in self.winfo_children():
            try:
                child.config(state='normal')
            except tk.TclError:
                self._enable(child)


    def setmetadatafile(self):
        """Sets the filepath of the  metadata file """
        filepath = tkfiledialog.askopenfilename(title='select metadata file',
                                                filetypes=(('json files', '*.json'),
                                                           ('all files', '*.*')))
        self.setfilepath(filepath)

    def setfilepath(self, filepath=None):
        if filepath:
            name = os.path.basename(filepath)
            self.metaname_label.config(text=name)
            self.metafilepath = os.path.abspath(filepath)
        else:
            self.metafilepath = None
            self.metaname_label.config(text='Not Selected')

    def on_select_pathology(self, event):
        strpathology = self.selected_pathology.get()
        if self.dc and self.dc.status_code == 200:
            self.dc_combox2.config(values=self.dc.get_pathology_versions(strpathology))
        self.dc_combox2.delete(0, 'end')
        self.dc_json = None

    def on_select_version(self, event):
        LOGGER.info('Retrieving metadata json')
        if self.dc and self.dc.status_code == 200:
            self.dc_json = self.dc.getjson(self.selected_pathology.get(),
                                           self.selected_version.get())

    def get_all_cdes(self):
        LOGGER.info('Trying to retrive cde metadata from Data Cataloge. Using DC url: {}'.format(DC_DOMAIN))
        all_pathologies_url = ''.join([DC_DOMAIN, DC_SUBDOMAIN_ALLPATHOLOGIES])
        r = requests.get(all_pathologies_url)
        self.dc = DcConnector(r)
        if self.dc.status_code == 200:
            self.dc_combox1.config(values=self.dc.pathology_names)
        elif 500 <= self.dc.status_code <= 599:
            LOGGER.info('Data Cataloge server internal error.')
        elif 400 <= self.dc.status_code <= 499:
            LOGGER.info('Data Cataloge could not be reach!. Please check DC_DOMAIN in config url')

    def save_2_disc(self):
        if self.dc_json:
            output_file = tkfiledialog.asksaveasfilename(title='enter file name',
                                                         defaultextension='.json',
                                                         filetypes=(('json files', '*.json'),
                                                                    ('all files', '*.*')))
            if output_file:
                with open(output_file, 'w') as jsonfile:
                    json.dump(self.dc_json, jsonfile)
                    tkmessagebox.showinfo(
                        title='Status info',
                        message='Schema file has been saved.'
                    )
            else:
                tkmessagebox.showerror(
                    title='File not found',
                    message='Please give an output file.'
                )
        else:
            tkmessagebox.showerror(
                title='Data Catalogue schema not found',
                message='Please select Data Catalogue schema.'
            )
