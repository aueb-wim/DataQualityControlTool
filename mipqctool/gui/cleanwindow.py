import tkinter as tk
from tkinter import ttk


class CleanWindow():
    def __init__(self, parent):
        self.parent = parent
        self.master = tk.Tk()
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.title('Data Cleaning Suggestions')
        self.__init()
        self.__packing()

    def __init(self):
        self.main_frame = tk.Frame(master=self.master, padx=2, pady=2)
        self.label1= tk.Label(self.main_frame, text='Select Column:')
        columns_with_corrections = [key  for key, columnreport in self.parent.reportcsv.columnreports.items() if len(columnreport.all_corrections) > 0]
        self.columns_cbox = ttk.Combobox(self.main_frame, width=35,                                    
                                         values=columns_with_corrections)
        self.columns_cbox.bind("<<ComboboxSelected>>", self.on_select_column)


        self.label2 = tk.Label(self.main_frame, text = 'Replacements')
        self.sugg_frame = tk.Frame(self.main_frame)
        self.sugg_scrollbar = tk.Scrollbar(self.sugg_frame)
        self.sugg_listbox = tk.Listbox(self.sugg_frame,
                                       yscrollcommand=self.sugg_scrollbar.set,
                                       width=35, height=10)
        self.sugg_scrollbar.config(command=self.sugg_listbox.yview)

    def __packing(self):
        self.main_frame.pack()
        self.label1.pack()
        self.columns_cbox.pack(padx=4, pady=4)
        self.label2.pack()
        self.sugg_frame.pack(fill='both', padx=4, pady=4)
        self.sugg_listbox.pack(side='left', fill='both')
        self.sugg_scrollbar.pack(side='left', fill=tk.Y)

    def on_select_column(self, event):
        if self.columns_cbox.current() > -1:
            sel_col = self.columns_cbox.get()
            self.__update_col_sugg(sel_col)
            

    def on_close(self):
        self.master.destroy()


    def __update_col_sugg(self, column):
        columnreport = self.parent.reportcsv.columnreports.get(column)
        self.sugg_listbox.delete(0,tk.END)
        all_corr = columnreport.all_corrections
        for item in all_corr:
            self.sugg_listbox.insert(all_corr.index(item), item)





