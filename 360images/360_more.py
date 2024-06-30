import piexif
from PIL import Image
from PIL.ExifTags import GPSTAGS


def extract_exif(image_file):
    try:
        exif_data = piexif.load(image_file)
        return exif_data
    except Exception as e:
        print(f"Error: {e}")
        return None



def get_decimal_from_dms(dms, ref):
    """
    Convert degrees, minutes, and seconds (DMS)
    to decimal format.
    """
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return degrees + minutes + seconds


def get_gps_coordinates(image_filename):
    """
    Extract GPS coordinates from an image and
    convert them to decimal format.
    """
    # Open image and extract EXIF data
    image = Image.open(image_filename)
    exif_data = image._getexif()

    # Ensure the image has GPS info
    if not exif_data or 34853 not in exif_data:
        return None, None

    # Extract GPS Info
    gps_info = {}
    for key in exif_data[34853].keys():
        decode = GPSTAGS.get(key, key)
        gps_info[decode] = exif_data[34853][key]

    # Get GPS Latitude and Longitude in DMS
    gps_latitude = gps_info.get('GPSLatitude')
    gps_latitude_ref = gps_info.get('GPSLatitudeRef')
    gps_longitude = gps_info.get('GPSLongitude')
    gps_longitude_ref = gps_info.get('GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and \
            gps_longitude and gps_longitude_ref:
        lat = get_decimal_from_dms(gps_latitude,
                                   gps_latitude_ref)
        lon = get_decimal_from_dms(gps_longitude,
                                   gps_longitude_ref)
        return lat, lon

    return None, None



if __name__ == "__main__":
    image_file = 'data/skybox.jpg'  # Replace with the path to your image file
    exif_data = extract_exif(image_file)

    if exif_data:
        for ifd_name in exif_data:
            print(f"IFD: {ifd_name}")

            try:  # avoid error for items that are bytes or missing
                for tag, value in exif_data[ifd_name].items():
                    tag_name = piexif.TAGS[ifd_name][tag]["name"]

                    print(f"{tag_name}: {value}")
            except:
                "N/A"
    else:
        print("Failed to extract EXIF data.")
    # run the app on an image file
    #image_filename = 'data/11_02_2024.jpg'
    #latitude, longitude = get_gps_coordinates(image_filename)
    #if latitude is not None and longitude is not None:
    #    print(f"Latitude: {latitude}, Longitude: {longitude}")
    #else:
    #    print("GPS information not found in image.")

