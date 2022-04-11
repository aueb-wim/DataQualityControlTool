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
        self.dname = None
        self.dcexcel_path = None
        self.__init()
        self.__packing()

    def __init(self):
        # Input  interface
        # Data Catalogue xlsx file (Labels and Button)
        self.dcexcelframe = tk.Frame(self)
        self.dcexcel_label = tk.Label(self.dcexcelframe, text='Data Catalogue Excel file:')
        self.dcexcelpath_label = tk.Label(self.dcexcelframe, text='Not selected',
                                          bg='white', pady=4, width=50)
        self.dload_button = tk.Button(self.dcexcelframe, text='Select File',
                                      command=self.load_dcexcel_file)

        
        self.dc_validation_frame = tk.Frame(self)
        self.validate_button = tk.Button(self.dc_validation_frame, text='Validate',
                                         command=self.validate_excel)

    def __packing(self):
        self.dcexcelframe.pack(fill='both', ipady=2, ipadx=2)
        self.dcexcel_label.pack(side='left', padx=2)
        self.dcexcelpath_label.pack(side='left')
        self.dload_button.pack(side='left', pady=2, padx=4, anchor='e')
        
        self.dc_validation_frame.pack(anchor='e')
        self.validate_button.pack(side='left', padx=4, anchor='se')

    
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
        excelvalidator = DcExcel(self.dcexcel_path)
        if excelvalidator.is_valid:
            tkmessagebox.showinfo('Validation Result', 'Everything looks ok.')
        else:
            if excelvalidator.invalid_enums:
                for var, enums in excelvalidator.invalid_enums.items():
                    LOGGER.info("Variable {} has invalid enumerations: {}".format(var, enums))
            if excelvalidator.doubl_conceptpaths:
                for var, conceptpath in excelvalidator.doubl_conceptpaths.items():
                    LOGGER.info("Variable {} has doublicate concept path: {}".format(var, conceptpath))

            tkmessagebox.showerror('Validation Result','Invalid file. For more info please look at the console')



    