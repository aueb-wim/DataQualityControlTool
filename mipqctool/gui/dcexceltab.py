from asyncio.log import logger
import os
from threading import Thread
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from mipqctool.model.dcatalogue.dcexcel import DcExcel
from mipqctool.config import LOGGER

class ValidateDcExcelTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dataset_code= tk.StringVar()
        self.dataset_name= tk.StringVar()
        self.dataset_version= tk.StringVar()
        self.dname = None
        self.dcexcel_path = None
        self.__init()
        self.__packing()

    def __init(self):
        # Input  interface
        # Data Catalogue xlsx file (Labels and Button)
        self.dcexcelframe = tk.LabelFrame(self, text='DC Excel Validation')
        self.dcexcel_label = tk.Label(self.dcexcelframe, text='Data Catalogue Excel file:')
        self.dcexcelpath_label = tk.Label(self.dcexcelframe, text='Not selected',
                                          bg='white', pady=4, width=50)
        self.dload_button = tk.Button(self.dcexcelframe, text='Select File',
                                      command=self.load_dcexcel_file)

        
        self.validate_button = tk.Button(self.dcexcelframe, text='Validate',
                                         command=self.validate_excel)

        self.dc2jsonframe = tk.LabelFrame(self, text='DC-excel 2 DC-json Conversion Menu')
        self.dataset_code_label = tk.Label(self.dc2jsonframe, text='Pathology Code:')
        self.dataset_name_label = tk.Label(self.dc2jsonframe, text='Pathology Name:')
        self.dataset_version_label = tk.Label(self.dc2jsonframe, text='Pathology Version:')
        self.dataset_code_input = tk.Entry(self.dc2jsonframe, width=15, textvariable=self.dataset_code)
        self.dataset_name_input = tk.Entry(self.dc2jsonframe, width=15, textvariable=self.dataset_name)
        self.dataset_version_input = tk.Entry(self.dc2jsonframe, width=5, textvariable=self.dataset_version)
        self.save_dcjson_button = tk.Button(self.dc2jsonframe, text='Convert to DC json',
                                            command=self.save_dc_json)
        self._disable(self.dc2jsonframe)

    def __packing(self):
        self.dcexcelframe.pack(fill='both', ipady=2, ipadx=2, padx=4, pady=2)
        self.dcexcel_label.grid(row=0, column=0, padx=2)
        self.dcexcelpath_label.grid(row=0, column=1, padx=2)
        self.dload_button.grid(row=0, column=2, sticky='e')
        
        self.validate_button.grid(row=1, column=2, padx=4, pady=2, sticky='e')


        self.dc2jsonframe.pack(ipady=2, ipadx=2, padx=4, pady=4, anchor='w')
        self.dataset_name_label.grid(row=0, column=0, sticky='w')
        self.dataset_name_input.grid(row=0, column=1, sticky='e')
        self.dataset_code_label.grid(row=1, column=0, sticky='w')
        self.dataset_code_input.grid(row=1, column=1, sticky='e')
        self.dataset_version_label.grid(row=2, column=0, sticky='w')
        self.dataset_version_input.grid(row=2, column=1, sticky='e')

        self.save_dcjson_button.grid(row=3, column=1)

    def save_dc_json(self):
        dataset_name = self.dataset_name.get()
        dataset_code = self.dataset_code.get()
        dataset_version = self.dataset_version.get()
        if not dataset_code or not dataset_name or not dataset_version:
                tkmessagebox.showwarning('Warning', 'Please fill dataset info!')
        else:
            filepath = tkfiledialog.asksaveasfilename(title='enter file name',
                                                  filetypes=(('json files', '*.json'),
                                                             ('all files', '*.*')))           
        
            with open(filepath, 'w') as jsonfile:
                jsonfile.write(self.__excelvalidator.create_dc_json(dataset_code, dataset_name, dataset_version))
            tkmessagebox.showinfo('Info', 'DC file saved successfully.')
            

        
    
    def load_dcexcel_file(self):
        """Loads the dataset csv"""
        filepath = tkfiledialog.askopenfilename(title='select DC Excel file',
                                                filetypes=(('xlsx files', '*.xlsx'),
                                                           ('all files', '*.*')))
        if filepath:
            self.dname = os.path.basename(filepath)
            self.dcexcelpath_label.config(text=self.dname)
            self.dcexcel_path = filepath
            self.validate_button.config(state='normal')


        else:
            self.dname = None
            self.dcexcel_label.config(text='Not Selected')

    def validate_excel(self):
        if self.dcexcel_path:
            LOGGER.info("Validating file: {}".format(self.dname))
            self.__excelvalidator = DcExcel(self.dcexcel_path)
            if self.__excelvalidator.is_valid:
                LOGGER.info('File "{}" is valid'.format(self.dname))
                tkmessagebox.showinfo('Validation Result', 'Everything looks ok.')
                self._enable(self.dc2jsonframe)

            else:
                if self.__excelvalidator.invalid_enums:
                    LOGGER.info("<--------Invalid enumerations-------->")
                    for var, enums in self.__excelvalidator.invalid_enums.items():
                        LOGGER.info("Variable {} has invalid enumerations: \n {}".format(var, enums))
                if self.__excelvalidator.doubl_conceptpaths:
                    LOGGER.info("<--------Dublicate Concept Paths-------->")
                    for var, conceptpath in self.__excelvalidator.doubl_conceptpaths.items():
                        LOGGER.info("Variable {} has doublicate concept path: \n {}".format(var, conceptpath))
                LOGGER.info("<--------General errors---------->")
                for var, errors in self.__excelvalidator.validation_errors.items():
                    errors_string = '\n' + '\n'.join(errors)
                    LOGGER.info('Variable "{}" has the following validation errors: {}'.format(var, errors_string))

                    self._disable(self.dc2jsonframe)
                    self.__excelvalidator = None

                tkmessagebox.showerror('Validation Result','Invalid file. For more info please look at the console')
        else:
            tkmessagebox.showerror('Error','Please select file, first.')

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




    