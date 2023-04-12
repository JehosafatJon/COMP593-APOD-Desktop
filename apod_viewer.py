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
    img_path = sel_info['file_path']
    
    # Resizes image
    unsized_img = Image.open(img_path)
    new_size = image_lib.scale_image(image_size=(unsized_img.width, unsized_img.height))
    resized_img = unsized_img.resize(new_size, Image.ANTIALIAS)
    
    # Configure Widgets
    global img_apod
    img_apod = ImageTk.PhotoImage(resized_img)
    lbl_image.configure(image=img_apod)
    lbl_desc.configure(text=sel_info['explanation'], wraplength=root.winfo_width(), justify="left")

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
    date = dentry_dateselect.get_date()

    if date < date.fromisoformat("1995-06-16"):
        print("Error: APOD date cannot be before 1995-06-16.")
        return
    elif date > date.today():
        print("Error: APOD date cannot be in the future.")
        return

    apod_desktop.add_apod_to_cache(date)
    
    box_imgselect.configure(values=apod_desktop.get_all_apod_titles())

    return

def resize(event):

    # TODO: make resizable

    return


# GUI Init
root = Tk()
root.title("Astronomy Picture of the Day Viewer")
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)

# Set Icon
app_id = 'APODViewer'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
root.iconbitmap(os.path.join(script_dir, "NASA Logo.ico"))

# Frames
frm_top = ttk.Frame(root)
frm_top.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

frm_mid = ttk.Frame(root)
frm_mid.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
frm_mid.columnconfigure(0, weight=1)
frm_mid.rowconfigure(0, weight=1)

frm_bot_left = ttk.LabelFrame(root, text="View Cached Image")
frm_bot_left.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="W")
frm_bot_left.columnconfigure(0, weight=1)
frm_bot_left.rowconfigure(0, weight=1)
frm_bot_left.rowconfigure(1, weight=1)
frm_bot_left.rowconfigure(2, weight=1)

frm_bot_right = ttk.LabelFrame(root, text="Get More Images")
frm_bot_right.grid(row=2, column=2, padx=5, pady=5, sticky=W)
frm_bot_right.columnconfigure(0, weight=1)
frm_bot_right.rowconfigure(0, weight=1)

# Widgets
# Top
img_apod = ImageTk.PhotoImage(file=os.path.join(script_dir, "NASA Logo Splash.png"))
lbl_image = ttk.Label(frm_top, image=img_apod)
lbl_image.grid(padx=10, pady=10)

# Mid
lbl_desc = ttk.Label(frm_mid, text="")
lbl_desc.grid(padx=20, pady=0, sticky="NSEW")


# Bot_Left
lbl_imgselect = ttk.Label(frm_bot_left, text= "Select Image:", width=12)
lbl_imgselect.grid(row=0, column=0, padx=5, pady=5, sticky=W)

box_imgselect = ttk.Combobox(frm_bot_left, width=40, state="readonly", values=apod_desktop.get_all_apod_titles())
box_imgselect.grid(row=0, column=1, padx=5, pady=5, sticky=W)
box_imgselect.set("Select an Image")
box_imgselect.bind("<<ComboboxSelected>>", handle_apod_sel)

btn_imgselect = ttk.Button(frm_bot_left, text="Set as Desktop", command=handle_set_desktop)
btn_imgselect.grid(row=0, column=2, padx=5, pady=5, sticky=W)

# Bot_Right
lbl_dateselect = ttk.Label(frm_bot_right, text= "Select Date:")
lbl_dateselect.grid(row=0, column=0, padx=5, pady=5)

dentry_dateselect = DateEntry(frm_bot_right, date_pattern="YYYY-MM-DD", state="readonly")
dentry_dateselect.grid(row=0, column=1, padx=5, pady=5)

btn_imgdownload = ttk.Button(frm_bot_right, text="Download Image", command=handle_download_Image)
btn_imgdownload.grid(row=0, column=2, padx=5, pady=5)

# GUI Loop
root.mainloop()