from tkinter import *
from tkinter import ttk
import inspect
import os
import apod_desktop

# Determine the path and parent directory of this script
script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
script_dir = os.path.dirname(script_path)

# Initialize the image cache
apod_desktop.init_apod_cache(script_dir)

# TODO: Create the GUI
root = Tk()
root.geometry('600x400')

frm_top = ttk.Frame(root)
frm_top.grid(row=0, column=0, columnspan=2)

frm_bottom = ttk.Frame(root)
frm_bottom.grid(row=0, column=0, columnspan=2)

lbl_date = ttk.Label(frm_bottom, text="Enter a Date (YYYY-MM-DD):")
lbl_date.grid(row=0, column=0, padx=(0,10), pady=10)

ent_date = ttk.Entry(frm_bottom)
ent_date.grid(row=0, column=1, padx=(0,10), pady=10)

root.mainloop()