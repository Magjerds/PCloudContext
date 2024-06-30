from PIL import Image
import io
import pyheif  # for HEIC file support
import exifread  # to extract EXIF data
import re  # for regex support
import os  # for file path and operating system compatibility

# Function to extract EXIF data from different image formats
def get_exif_data(ifile):
    data = None
    if re.search(r'heic$', str(ifile), re.IGNORECASE):  # Specifically for HEIC files
        try:
            heif_file = pyheif.read_heif(str(ifile))
            for metadata in heif_file.metadata:
                if metadata['type'] == 'Exif':
                    fstream = io.BytesIO(metadata['data'][6:])
                    tags = exifread.process_file(fstream, details=False)
                    data = (str(tags.get("Image Make", '')), str(tags.get("Image Model", '')), str(tags.get('EXIF DateTimeOriginal', '')), ifile)
        except Exception as e:
            print(f"Error reading HEIC file {ifile}: {str(e)}")
    else:
        print(f"Unsupported file format or file is corrupt: {ifile}")
    
    return data

# Function to log extracted data
def log_data(data, logfile):
    if data:
        make, model, date_gen, image_name = data
        logfile.write(f"{make},{model},{date_gen},{os.path.basename(image_name)}\n")

if __name__ == "__main__":
    logfile = open('imagelog.txt', 'w')  # Open log file in write mode to record data

    image_path = 'data/Feb11at8-03PM-poly2/1707678236902768.heif'
    image_path = 'data/Feb11at8-03PM-poly2/1707678262139085.heif'
    isfile = os.path.isfile(image_path)
    if isfile:
        exif_data = get_exif_data(image_path)
        if exif_data:
            log_data(exif_data, logfile)
    else:
        print(f"File does not exist: {image_path}")

    logfile.close()  # Close the log file
    print("Processing complete. Extracted data is stored in imagelog.txt.")
