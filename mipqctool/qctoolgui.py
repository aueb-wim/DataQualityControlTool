#!/usr/bin/env python3
import os
import logging
from tkinter import ttk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from .texthandler import TextHandler
from .gui import CsvTab, DicomTab
from . import __version__
from .config import LOGGER, C_FORMAT

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        self.__init()
        # initialize logger for console
        text_handler = TextHandler(self.st)
        text_handler.setFormatter(C_FORMAT)
        text_handler.setLevel(logging.INFO)
        LOGGER.addHandler(text_handler)

    def __init(self):
        """Draw the widgets"""
        # Create a controller for tabs
        self.tabcontrol = ttk.Notebook(self.master)
        # Create the tab for tabular datasets processing
        self.tabframe = CsvTab()
        self.tabframe2 = DicomTab()

        # add the tab for tabular quality control into the main frame
        self.tabcontrol.add(self.tabframe, text='Tabular QC')
        self.tabcontrol.add(self.tabframe2, text='Dicom QC')

        # add console window 
        self.bottomframe = tk.Frame(self.master, height=20)
        self.terminallabel = tk.Label(self.bottomframe, text='Console output:')
        self.st = ScrolledText(self.bottomframe, state='disabled', height=10)
        self.st.configure(font='TkFixedFont')
        self.__packing()

    def __packing(self):
        """arrange the widgets"""
        self.pack(expand=0)
        self.tabcontrol.pack(fill='both', expand=1)
        self.bottomframe.pack(side='bottom', fill='both')
        self.terminallabel.pack(side='top', anchor='w')
        self.st.pack(side='bottom', fill='both')

def main():
    """Main application window"""
    root = tk.Tk()
    app = Application(master=root)
    app.master.title('HBP-MIP Data Quality Control Tool  version %s'
                     % __version__)
    app.master.resizable(False, False)
    app.mainloop()


if __name__ == '__main__':
    main()
