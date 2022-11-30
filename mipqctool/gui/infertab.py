from asyncio.log import logger
import os
from threading import Thread
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from mipqctool.controller import InferSchema
from mipqctool.gui.inferoptionsframe import InferOptionsFrame
from mipqctool.config import LOGGER


class InferTab(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # set default option for json metadata type to Frictionless
        self.schema_output = tk.IntVar()
        self.schema_output.set(1)
        self.schema_outputs = [('DC (xlsx)', 1), ('QC (json)', 2)]
        self.__init()
        self.__packing()

    def __init(self):

        # Input dataset interface
        # Dataset file (Labels and Button)
        self.datasetframe = tk.Frame(self)
        self.dataset_label = tk.Label(self.datasetframe, text='Dataset file:')
        self.datasetpath_label = tk.Label(self.datasetframe, text='Not selected',
                                          bg='white', pady=4, width=50)
        self.dload_button = tk.Button(self.datasetframe, text='Select File',
                                      command=self.loaddatasetfile)
        
        self.inf_opt_frame = InferOptionsFrame(self)
        
        # #### OUTPUT OPTIONS ####
        self.output_frame = tk.Frame(self)
        self.schema_spec_lbframe = tk.LabelFrame(self.output_frame, text='Schema output')
        self.excel_radiobutton = tk.Radiobutton(self.schema_spec_lbframe,
                                                  text='Data Catalogue (xlsx)',
                                                  variable=self.schema_output,
                                                  value=1)
        self.frictionless_radiobutton = tk.Radiobutton(self.schema_spec_lbframe,
                                                  text='Frictionless (json)',
                                                  variable=self.schema_output,
                                                  value=2)
        self.save_button = tk.Button(self.output_frame, text='Save Schema',
                                     command=self.threaded_save_schema)

    def __packing(self):

        self.datasetframe.pack(fill='both', ipady=2, ipadx=2)
        self.dataset_label.pack(side='left', padx=2)
        self.datasetpath_label.pack(side='left')
        self.dload_button.pack(side='left', pady=2, padx=4, anchor='e')


        # #### INFER OPTIONS ####
        self.inf_opt_frame.pack(fill='both', ipadx=2, ipady=2)
        

        # #### OUTPUT OPTIONS ####
        self.output_frame.pack(anchor='e')
        self.schema_spec_lbframe.pack(side='left')
        self.excel_radiobutton.pack(anchor='w')
        self.frictionless_radiobutton.pack(anchor='w')
        self.save_button.pack(side='left', padx=4, anchor='se')

    def threaded_save_schema(self):
        t1=Thread(target=self.save_schema)
        t1.start()


    def save_schema(self):
        self.save_button.config(state='disabled')
        if self.inf_opt_frame.cde_dict:
            self.schema_output.set(1)

        if self.schema_output.get() == 1:
            output_file = tkfiledialog.asksaveasfilename(title='enter file name',
                                                        filetypes=(('excel files', '*.xlsx'),
                                                                    ('all files', '*.*')))
        else:
            output_file = tkfiledialog.asksaveasfilename(title='enter file name',
                                                        filetypes=(('json files', '*.json'),
                                                                    ('all files', '*.*')))

        if output_file:
            warningtitle = 'Can not save the schema'
            if not self.dname:
                tkmessagebox.showwarning(warningtitle,
                                         'Please, select dataset file')
            max_categories = int(self.inf_opt_frame.max_categories.get())
            sample_rows = int(self.inf_opt_frame.sample_rows.get())
            na_empty_strings_only = self.inf_opt_frame.na_empty_strings_only.get()
            if self.inf_opt_frame.cde_dict:
                infer = InferSchema.from_disc(self.datasetpath, 
                                              sample_rows=sample_rows,
                                              maxlevels=max_categories,
                                              cdedict=self.inf_opt_frame.cde_dict,
                                              na_empty_strings_only=na_empty_strings_only)
                if len(infer.invalid_nominals) > 0:
                    for key, value in infer.invalid_nominals.items():
                        LOGGER.info('Column {} contains invalid code enumerations {}'.format(key, value))
                    tkmessagebox.showerror('Invalid nominal codes',
                                           'The file contains columns with invalid nominal codes. \n For more info please see at the console below')
                    return

                if self.inf_opt_frame.thresholdstring.get() == '':
                    threshold = 0.6
                else:
                    threshold = float(self.inf_opt_frame.thresholdstring.get())
                LOGGER.info('CDE similarity threshold: %f' % threshold)
                infer.suggest_cdes(threshold=threshold)
                infer.export2excel(output_file)
                LOGGER.info('Schema file has been created successully')
                tkmessagebox.showinfo(
                        title='Status info',
                        message='Schema file has been created successully'
                    )
  
            else: 
                infer = InferSchema.from_disc(self.datasetpath, 
                                              sample_rows=sample_rows,
                                              maxlevels=max_categories,
                                              cdedict=None,
                                              na_empty_strings_only=na_empty_strings_only)
                if len(infer.invalid_nominals) > 0:
                    for key, value in infer.invalid_nominals.items():
                        LOGGER.info('Column {} contains invalid code enumerations {}'.format(key, value))
                    tkmessagebox.showerror('Invalid nominal codes',
                                           'The file contains columns with invalid nominal codes. \n For more info please see at the console below')
                    return
                if len(infer.invalid_header_names) > 0:
                    for name in infer.invalid_header_names:
                        LOGGER.info('Column {} has an invalid name.'.format(name))
                    tkmessagebox.showerror('Invalid column names',
                                           'The file contain columns with invalid names. For more info please see at the console below')
                if self.schema_output.get() == 1:
                    infer.export2excel(output_file)
                    LOGGER.info('Schema file has been created successully')
                    tkmessagebox.showinfo(
                        title='Status info',
                        message='Schema file has been created successully'
                    )
                else:
                    infer.expoct2qcjson(output_file)
                    LOGGER.info('Schema file has been created successully')
                    tkmessagebox.showinfo(
                        title='Status info',
                        message='Schema file has been created successully'
                    )
        self.save_button.config(state='normal')


    def loaddatasetfile(self):
        """Loads the dataset csv"""
        filepath = tkfiledialog.askopenfilename(title='select dataset file',
                                                filetypes=(('csv files', '*.csv'),
                                                           ('all files', '*.*')))
        if filepath:
            self.dname = os.path.basename(filepath)
            self.datasetpath_label.config(text=self.dname)
            self.datasetpath = filepath
            self.save_button.config(state='normal')

        else:
            self.dname = None
            self.datasetpath_label.config(text='Not Selected')


