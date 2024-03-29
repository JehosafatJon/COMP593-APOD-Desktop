'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''

import requests as rq

def main():
    # TODO: Add code to test the functions in this module

    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    
    # API request from NASA APOD
    
    query_params = {
        "date" : apod_date,
        "api_key" : '0WyzluYR1DMfXlmbJaM4pwlD30MYk4ULWTde6cCh',
        "thumbs" : True
    }
    response = rq.get('https://api.nasa.gov/planetary/apod', query_params)

    # Checks for successful info retrieval
    
    print(f"Getting {apod_date} information from NASA ... ", end="")
    if response.ok:
        print("Successful.")
        return response.json()
    else:
        print("Unsuccessful.")
        return

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    
    # Determines if media is picture or image and returns appropriate URL

    if apod_info_dict["media_type"] == 'image':
        url = apod_info_dict["hdurl"]
    
    elif apod_info_dict["media_type"] == 'video':
        url = apod_info_dict["thumbnail_url"]
        
    return url

if __name__ == '__main__':
    main()