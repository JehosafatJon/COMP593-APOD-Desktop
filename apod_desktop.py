""" ~~~ Jonathan Hughes COMP593 ~~~~~~
               __
              / _) < woohoo python!
     _.----._/ /
    /         /
 __/ (  | (  |
/__.-'|_|--|_|   
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

COMP 593 - Final Project: APOD Desktop

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

from datetime import date
import os
import image_lib
import inspect
from sys import argv
import re
import apod_api
import sqlite3
import hashlib

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    # Sets the APOD date to today by default
    apod_date = date.today()

    # If a command line parameter is provided, 
    # check format, validity, and APOD date range.
    if len(argv) - 1 >= 1:
        apod_date = argv[1]
        
        if not re.match(r"\d{4}-\d\d-\d\d", apod_date):
            print("Invalid Date Format! The correct format is YYYY-MM-DD")
            exit()

        try:
            apod_date = date.fromisoformat(apod_date)
        except ValueError as err:
            print(f"Error: {err}")
            exit()

        if apod_date < date.fromisoformat("1995-06-16"):
            print("Error: APOD date cannot be before 1995-06-16.")
            exit()
        elif apod_date > date.today():
            print("Error: APOD date cannot be in the future.")
            exit()
        
    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir
    global image_cache_db
    
    #Determine the path of the image cache directory
    
    image_cache_dir = f"{parent_dir}\\image_cache_directory"
    print(f"Image Cache Directory: {image_cache_dir}")

    # Create the image cache directory if it does not already exist
    
    print("Image Cache Directory ... ", end="")
    if not os.path.exists(image_cache_dir):
        os.mkdir(image_cache_dir)
        print("Created.")
    else:
        print("Already exists.")

    # Determine the path of image cache DB

    image_cache_db = f"{image_cache_dir}\\image_cache.db"
    print(f"Image Cache DB: {image_cache_db}")

    # Create the DB if it does not already exist

    print("Image Cache DB ... ", end="")
    if not os.path.exists(image_cache_db):
        con = sqlite3.connect(image_cache_db)
        cur = con.cursor()
        
        create_db_query = """
            CREATE TABLE IF NOT EXISTS images
            (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                explanation TEXT NOT NULL,
                path TEXT NOT NULL,
                hash TEXT NOT NULL,
            );
        """

        cur.execute(create_db_query)
        con.commit()
        con.close()
        print("Created.")
    else:
        print("Already exists.")

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print("APOD date:", apod_date)
    
    # Download the APOD information from the NASA API
    
    apod_dict = apod_api.get_apod_info(apod_date)
    print(f"APOD Title: {apod_dict['title']}")

    # Determine the APOD image url
    
    img_url = apod_api.get_apod_image_url(apod_dict)
    if img_url == "":
        print("APOD has no image URL.")
        return 0
    print(f"APOD URL: {img_url}")

    # Download the APOD image

    img_data = image_lib.download_image(img_url)
    if img_data is None:
        return 0

    # Get the SHA-256 hash of the downloaded APOD image

    img_hash = hashlib.sha256(img_data).hexdigest()
    print(f"APOD SHA-256: {img_hash}")
    
    # Check whether the APOD already exists in the image cache.
    # If the APOD already exists, returns the existing APOD ID,
    # And does not proceed to save the file again.
    
    print("Checking if APOD exists in cache ... ", end="")
    apod_id = get_apod_id_from_db(img_hash)
    if apod_id != 0:
        print("APOD already exists in cache.")
        return apod_id
    print("APOD does not exist in cache.")

    # Determine the APOD image file path to save

    img_path = determine_apod_file_path(apod_dict["title"], img_url)
    print(f"APOD Image Path: {img_path}")

    # Save the APOD file to the image cache directory

    print(f"Saving APOD image as {img_path} ... ", end="")
    if not image_lib.save_image_file(img_data, img_path):
        print("Unsuccessful.")
        return 0
    print("Successful.")
    
    # Add the APOD information to the DB

    print("Adding APOD to DB ... ", end="")
    new_apod_id = add_apod_to_db(apod_dict["title"], apod_dict["explanation"], img_path, img_hash)    
    if new_apod_id == 0:
        print("Unsuccesful.")
        return 0
    print("Succesful.")
    return new_apod_id

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    
    # Connects and Inserts data into the APOD cache DB

    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()

    add_apod_query = """
    INSERT INTO images
    (
    title,
    explanation,
    path,
    hash
    )
    VALUES (?, ?, ?, ?);
    """
    
    new_apod = (
        title,
        explanation,
        file_path,
        sha256
    )

    try:
        cur.execute(add_apod_query, new_apod)
    except:
        return 0 
    
    con.commit()

    # Queries for the ID of the added APOD

    id_query =f"""
    SELECT id FROM images
    WHERE title = "{title}"
    """

    cur.execute(id_query)
    apod_id = cur.fetchone()[0]
    con.close()

    return apod_id

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    
    # Queries the DB for all entries' ID and hash

    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()

    hash_query = """
        SELECT id, hash FROM images
    """

    cur.execute(hash_query)
    db_entries = cur.fetchall()
    cur.close()

    # Checks each entry's hash against the current APOD hash
    # If matches, returns that entry's ID

    for entry in db_entries:
        if entry[1] == image_sha256:
            return entry[0]

    return 0

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    
    # Gets the image extension from the URL,
    # Replaces non-word characters with nothing after 
    # Replacing spaces with underscores in the APOD title,
    # Joins and returns full image path

    img_ext = image_url.split('.')[-1]
    img_file_name = re.sub(r"\W+", "", re.sub(" ", "_", image_title.strip()))
    
    return f"{image_cache_dir}\\{img_file_name}.{img_ext}"

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    
    # Query DB for image info

    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()

    info_query = f"""
        SELECT title, explanation, path FROM images
        WHERE id = '{image_id}';
    """

    cur.execute(info_query)
    info = cur.fetchone()
    con.close()

    # Put information into a dictionary
    
    apod_info = {
        'title': info[0], 
        'explanation': info[1],
        'file_path': info[2],
    }
   
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    # TODO: Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    
    info_query = f"""
        SELECT title FROM images;
    """

    cur.execute(info_query)
    all_apods = cur.fetchall()
    con.close()
    
    return [title[0] for title in all_apods]

if __name__ == '__main__':
    main()