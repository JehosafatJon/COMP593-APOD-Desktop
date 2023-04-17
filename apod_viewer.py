""" ~~~ Jonathan Hughes COMP593 ~~~~~~
               __
              / _) < that's hot.
     _.----._/ /
    /         /
 __/ (  | (  |
/__.-'|_|--|_|   
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

COMP 593 - Final Project 
  BONUS: APOD Desktop GUI!

Description: 
  A cool, fancy and HOT GUI for the
  NASA APOD Desktop application!

Usage:
  python apod_viewer.py

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

from tkinter import *
from tkinter import ttk
import inspect
import os
import apod_desktop
import image_lib
import ctypes
from PIL import ImageTk, Image
from tkcalendar import DateEntry
from datetime import date


# Determine the path and parent directory of this script
script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
script_dir = os.path.dirname(script_path)

# Initialize the image cache
apod_desktop.init_apod_cache(script_dir)

# Event Handlers

def handle_apod_sel(event):
    # Selection from dropdown box
    sel_apod = box_imgselect.current() + 1
    
    # Gets info from database
    sel_info = apod_desktop.get_apod_info(sel_apod)
    global img_path
    img_path = sel_info['file_path']
    
    
    # Resizes image
    global unsized_img
    unsized_img = Image.open(img_path)
    new_size = image_lib.scale_image(image_size=(unsized_img.width, unsized_img.height), max_size=(root.winfo_width(), frm_top.winfo_height()))
    resized_img = unsized_img.resize(new_size)
    
    # Configure Widgets
    global img_apod
    img_apod = ImageTk.PhotoImage(resized_img)
    lbl_image.configure(image=img_apod)
    lbl_desc.configure(text=sel_info['explanation'], wraplength=frm_mid.winfo_width(), justify="left")

    return

def handle_set_desktop():
    
    if box_imgselect.current() == -1:
        return

    sel_apod = box_imgselect.current() + 1

    sel_info = apod_desktop.get_apod_info(sel_apod)
    img_path = sel_info['file_path']
    image_lib.set_desktop_background_image(img_path)

    return

def handle_download_Image():
    date_entry = dentry_dateselect.get_date()

    apod_desktop.add_apod_to_cache(date_entry)
    
    box_imgselect.configure(values=apod_desktop.get_all_apod_titles())

    return

def resize(event):
    # TODO: make resizable
    
    # Description Label
    global lbl_desc
    lbl_desc.configure(wraplength=lbl_desc.winfo_width())

    # Resize Image
    #new_size = image_lib.scale_image(image_size=(unsized_img.width, unsized_img.height), max_size=(root.winfo_width(), root.winfo_height()))
    #resized_img = unsized_img.resize(new_size)

    # Configure Widgets
    global img_apod
    #img_apod = ImageTk.PhotoImage(resized_img)
    #lbl_image.configure(image=img_apod)


    return


# GUI Init
root = Tk()
root.title("Astronomy Picture of the Day Viewer")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.bind("<Configure>", resize)


# Set Icon
app_id = 'APODViewer'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
root.iconbitmap(os.path.join(script_dir, "NASA Logo.ico"))

# Frames
frm_top = ttk.Frame(root)
frm_top.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=N)

frm_mid = ttk.Frame(root)
frm_mid.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="SEW")
frm_mid.columnconfigure(0, weight=1)
frm_mid.rowconfigure(0, weight=1)

frm_bot_left = ttk.LabelFrame(root, text="View Cached Image")
frm_bot_left.grid(row=2, column=0, padx=5, pady=5, sticky=NSEW)
frm_bot_left.columnconfigure(0, weight=0)
frm_bot_left.columnconfigure(1, weight=1)
frm_bot_left.columnconfigure(2, weight=0)
frm_bot_left.rowconfigure(0, weight=1)

frm_bot_right = ttk.LabelFrame(root, text="Get More Images")
frm_bot_right.grid(row=2, column=1, padx=5, pady=5, sticky=NSEW)
frm_bot_right.columnconfigure(0, weight=0)
frm_bot_right.columnconfigure(1, weight=1)
frm_bot_right.columnconfigure(1, weight=0)
frm_bot_right.rowconfigure(0, weight=1)

# Widgets
# Top
img_apod = ImageTk.PhotoImage(file=os.path.join(script_dir, "NASA Logo Splash.png"))
lbl_image = ttk.Label(frm_top, image=img_apod)
lbl_image.grid(padx=0, pady=0, sticky=NSEW)

# Mid
lbl_desc = ttk.Label(frm_mid)
lbl_desc.grid(padx=20, pady=0, sticky=NSEW)

# Bot_Left
lbl_imgselect = ttk.Label(frm_bot_left, text= "Select Image:", width=12)
lbl_imgselect.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW)

box_imgselect = ttk.Combobox(frm_bot_left, state="readonly", values=apod_desktop.get_all_apod_titles())
box_imgselect.grid(row=0, column=1, padx=5, pady=5, sticky=NSEW)
box_imgselect.set("Select an Image")
box_imgselect.bind("<<ComboboxSelected>>", handle_apod_sel)

btn_imgselect = ttk.Button(frm_bot_left, text="Set as Desktop", command=handle_set_desktop)
btn_imgselect.grid(row=0, column=2, padx=5, pady=5, sticky=E)

# Bot_Right
lbl_dateselect = ttk.Label(frm_bot_right, text= "Select Date:")
lbl_dateselect.grid(row=0, column=0, padx=5, pady=5)

dentry_dateselect = DateEntry(frm_bot_right, date_pattern="YYYY-MM-DD", state="readonly", mindate=date.fromisoformat("1996-05-16"), maxdate=date.today())
dentry_dateselect.grid(row=0, column=1, padx=5, pady=5)

btn_imgdownload = ttk.Button(frm_bot_right, text="Download Image", command=handle_download_Image)
btn_imgdownload.grid(row=0, column=2, padx=5, pady=5)

# GUI Loop
root.mainloop()