#!/usr/bin/env python3
import os
import logging
import queue

from tkinter import ttk, N, S, E, W
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from mipqctool.gui import CsvTab, DicomTab, InferTab, MappingTab
from mipqctool import __version__
from mipqctool.config import LOGGER, C_FORMAT, debug

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

class QueueHandler(logging.Handler):
    """Class to send logging records to a queue
    It can be used from different threads
    The ConsoleUi class polls this queue to display records in a ScrolledText widget
    """
    # Example from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    # (https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe!
    # See https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        self.scrolled_text.pack(side='bottom', fill='both', expand='yes')
        #self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.queue_handler.setFormatter(formatter)
        LOGGER.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)


class Application(tk.Frame):

    def __init__(self, master=None, logger=None):
        super().__init__(master)
        self.logger = logger
        self.__init()

    def __init(self):
        """Draw the widgets"""

        # add console window and logger
        self.bottomframe = tk.Frame(self.master, height=20)
        self.terminallabel = tk.Label(self.bottomframe, text='Console output:')
        self.console = ConsoleUi(self.bottomframe)
        #self.st = ScrolledText(self.bottomframe, state='disabled', height=10)
        #self.st.configure(font='TkFixedFont')
        # initialize logger for console
        #text_handler = TextHandler(self.st)
        #text_handler.setFormatter(C_FORMAT)
        #text_handler.setLevel(logging.DEBUG)
        #LOGGER.addHandler(text_handler)

        # Create a controller for tabs
        self.tabcontrol = ttk.Notebook(self.master)
        # Create the tab for tabular datasets processing
        self.tabframe = CsvTab()
        self.tabframe2 = DicomTab()
        self.tabframe3 = InferTab()
        self.tabframe4 = MappingTab()

        # add the tab for tabular quality control into the main frame
        self.tabcontrol.add(self.tabframe, text='Tabular QC')
        self.tabcontrol.add(self.tabframe3, text='Infer Dataset Schema')
        self.tabcontrol.add(self.tabframe2, text='Dicom QC')
        self.tabcontrol.add(self.tabframe4, text='Data Mapping')

        self.__packing()

    def __packing(self):
        """arrange the widgets"""
        self.pack(expand=0)
        self.tabcontrol.pack(fill='both', expand=1)
        self.bottomframe.pack(side='bottom', fill='both')
        self.terminallabel.pack(side='top', anchor='w')
        #self.st.pack(side='bottom', fill='both')
        #self.console.pack(side='bottom', fill='both')


def main():
    """Main application window"""
    root = tk.Tk()
    app = Application(master=root, logger=LOGGER)
    app.master.title('HBP-MIP Data Quality Control Tool  version %s'
                     % __version__)
    app.master.resizable(0, 0)
    app.mainloop()


if __name__ == '__main__':
    main()
