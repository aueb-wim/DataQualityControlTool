#!/usr/bin/env python3
""" This python script is not for normal use. It's only
use is for producing a windows executable with pyinstaller
"""
from multiprocessing import freeze_support
from mipqctool.__main__ import main

if __name__ == '__main__':
    freeze_support()
    main()
