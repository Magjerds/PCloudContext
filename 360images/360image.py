from PIL import Image
import os
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def get_gps_location(image_path):
    exif_data = get_exif_data(image_path)
    gps_info = exif_data.get("GPSInfo", {})
    
    if gps_info:
        gps_latitude = gps_info.get("GPSLatitude")
        gps_latitude_ref = gps_info.get("GPSLatitudeRef")
        gps_longitude = gps_info.get("GPSLongitude")
        gps_longitude_ref = gps_info.get("GPSLongitudeRef")

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

            return lat, lon
    return None

def convert_to_degrees(value):
    """Helper function to convert GPS coordinates to degrees."""
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)


def get_all_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            exif_data[decoded] = value
    return exif_data


image_path = 'data/IMG_9036.JPG'
print(os.path.isfile(image_path))
exif_data = get_all_exif_data(image_path)
print("Exif data for", image_path)
for tag, value in exif_data.items():
    print(f"{tag}: {value}")

print("\nGPS data for", image_path)
location = get_gps_location(image_path)
if location:
    print("Latitude:", location[0], "Longitude:", location[1])
else:
    print("GPS data not available.")
