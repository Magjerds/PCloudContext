import pyheif
import traceback

def read_heic_file(file_path):
    try:
        heif_file = pyheif.read(file_path)
        print(f"Successfully read the HEIC file: {file_path}")
        print(f"File details: Size - {heif_file.size}, Mode - {heif_file.mode}, Metadata - {len(heif_file.metadata)} items")
    except Exception as e:
        print(f"Failed to read the HEIC file: {file_path}")
        print("Error details:")
        traceback.print_exc()

if __name__ == "__main__":
    test_file_path = 'data/Feb11at8-03PM-poly2/1707678236902768.heif'  # Replace with the path to your HEIC file
    read_heic_file(test_file_path)
