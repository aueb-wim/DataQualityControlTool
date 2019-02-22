#!/usr/bin/env python3
""" This python script is not for normal use. It's only
use is for producing a windows executable with pyinstaller
"""

from mipqctool.qctoolgui import Application
from mipqctool import __version__
import tkinter as tk
from multiprocessing import freeze_support


def main():
    """Main application window"""
    root = tk.Tk()
    app = Application(master=root)
    app.master.title("HBP-MIP Data Quality Control Tool  version %s"
                     % __version__)
    app.master.resizable(False, False)
    app.mainloop()


if __name__ == '__main__':
    freeze_support()
    main()
