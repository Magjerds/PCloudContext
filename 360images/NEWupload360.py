from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap
import json
from detection.connect import init_cognite_connect
import math
import io
import uuid
import os
import numpy as np
from scipy.spatial.transform import Rotation as R


def adjust_image(image_path):
    image = Image.open(image_path)

    # Since the original image is rotated, its width becomes the height and vice versa
    original_width, original_height = image.size

    # Define the dimensions for the square image (768x768)
    target_size = 768

    # Calculate the top and bottom margins to crop
    margin = (original_height - target_size) // 2

    # Crop the image to the desired size
    cropped_image = image.crop((0, margin, original_width, original_height - margin))
    #cropped_image.show()
    return cropped_image


def adjust_to_mesh(camera_matrix, mesh_info_path, ):
    """
    Camera matrix: 4x4 transformation matrix
    """
    with open(mesh_info_path, 'r') as mesh_info:
        mesh_info = json.load(mesh_info)
    
    alignment_transform = np.array(mesh_info['alignmentTransform']).reshape((4, 4))
    #When going from image to model we don't inverse transform, only transform
    adjusted_camera_transformation_matrix = np.dot(alignment_transform, camera_matrix)

    y_alignment = mesh_info['yAlignmentRotation']
    y_alignment_matrix = np.array([
        [np.cos(y_alignment), 0, np.sin(y_alignment), 0],
        [0, 1, 0, 0],
        [-np.sin(y_alignment), 0, np.cos(y_alignment), 0],
        [0, 0, 0, 1]
    ])
    fully_adjusted_camera_transformation_matrix = np.dot(y_alignment_matrix, adjusted_camera_transformation_matrix)
    return  fully_adjusted_camera_transformation_matrix

def adjust_coordinate_system_transformation(matrix):
    """
    Adjusts the camera transformation matrix from Y-up to Z-up system
    and applies necessary 180-degree rotations around Z and X axes.

    Args:
    - matrix (numpy array): The original 4x4 transformation matrix.

    Returns:
    - numpy array: The adjusted 4x4 transformation matrix.
    """
    # Define the rotation to swap Y and Z axes and apply 180-degree rotations
    # Rotation to swap Y (up) and Z (up in target)
    # Additionally rotate 180 degrees around X to fix top and bottom flip
    # and 180 degrees around Z to correct left and right swap
    #swap_yz_rotate_xz = R.from_euler('xzx', [180, 90, 180], degrees=True) #Not working, visualized 180degrees opposite direction
    
    # Define the rotation to swap Y and Z axes and apply necessary corrections
    # Rotate 270 degrees around X to swap Y and Z and fix top and bottom flip
    # Rotate 180 degrees around Z to adjust for the XY-plane rotation
    #swap_yz_fix_flip_and_rotate_xy = R.from_euler('zx', [270, 180], degrees=True)


    # Apply this transformation to the rotation part of the matrix
    #rotation_matrix = matrix[:3, :3]
    #transformed_rot_matrix = swap_yz_rotate_xz.apply(rotation_matrix)
    
    # Replace the rotation part in the original matrix
    #adjusted_matrix = np.copy(matrix)
    #adjusted_matrix[:3, :3] = transformed_rot_matrix
    
    # No need to adjust translation if it's already scaled and just needs the rotation
    # If translation needs to be adjusted (e.g., scaling or further flipping), modify as needed
    # return adjusted_matrix
    return matrix


def prepare_and_upload_image(c, front_image_path, json_file_path, dummy_images_folder, mesh_info_path):
    """
    Prepare and upload the cubemap images and metadata to CDF.
    """
    # Adjust the front image
    front_image = adjust_image(front_image_path)

    # Prepare the cubemap images
    sides = ['back', 'left', 'right', 'top', 'bottom']
    cubemap_images = [front_image] + [Image.open(f"{dummy_images_folder}/{side}.jpg") for side in sides]

    # Extract metadata from the JSON file
    with open(json_file_path, 'r') as json_file:
        metadata = json.load(json_file)
    main_image_name, _ = os.path.splitext(os.path.basename(front_image_path))
    dataset_id = 8083603325410370

    for image, face in zip(cubemap_images, ['front'] + sides):
        file_metadata = {
            "site_id": "ntnu-lab",
            "site_name": "ntnu-360-maiken",
            "station_id": f"polycam-{main_image_name}", #should be unique for every picture
            "station_name": f"Adjusted Polycam images: {main_image_name}", #Unique for every image
            "image_type": "cubemap",
            "image_resolution": "768",
            "face": face
        }
        # Assume function to upload file to CDF
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()  # Get the byte value of the image
        external = str(uuid.uuid4())
        c.files.upload_bytes(
            content=img_byte_arr,
            name= f"{face}-image-{external}",
            external_id=f"{face}-image-{external}",  # Optionally, define an external ID
            mime_type="image/jpeg",
            metadata=file_metadata,
            data_set_id=dataset_id
        )
    
    #Calculations in mm
    camera_matrix = np.array([
        [metadata["t_00"], metadata["t_01"], metadata["t_02"], metadata["t_03"]*1000],
        [metadata["t_10"], metadata["t_11"], metadata["t_12"], metadata["t_13"]*1000],
        [metadata["t_20"], metadata["t_21"], metadata["t_22"], metadata["t_23"]*1000],
        [0, 0, 0, 1]
    ])
   
    adjusted_camera_matrix = adjust_to_mesh(camera_matrix, mesh_info_path)
    #Rotate around x-axis in order to move Y-axis with Z-axis
    rotate_around_x = np.array([
        [1, 0, 0, 0],
        [0, 0, -1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ])
    adjusted_coordinate_matrix = np.dot(adjusted_camera_matrix,rotate_around_x) 
    #rotation_180_y = np.array([
    #    [-1, 0, 0, 0],
    #    [0, 1, 0, 0],
    #    [0, 0, -1, 0],
    #    [0, 0, 0, 1]
    #])
    # Create a reflection matrix that inverts X and Y
    reflection_matrix = np.array([
        [-1, 0, 0, 0],  # Invert X
        [0, -1, 0, 0],  # Invert Y
        [0, 0, 1, 0],   # Keep Z
        [0, 0, 0, 1]    # Homogeneous coordinate
    ])
    adjusted_coordinate_matrix = np.dot(adjusted_coordinate_matrix, reflection_matrix)
  
    
    
    translation = adjusted_coordinate_matrix[:3, 3]
    rotation = R.from_matrix(adjusted_coordinate_matrix[:3, :3])
    rotation_vector = rotation.as_rotvec()
    angle = np.linalg.norm(rotation_vector)
    rotation_axis = rotation_vector/ (angle if angle != 0 else rotation_vector)
    angle_degrees = np.degrees(angle)

    
    # Event metadata including adjusted rotation
    event_metadata = {
        "site_id": "ntnu-lab",
        "site_name": "ntnu-360-maiken",
        "station_id": f"polycam-{main_image_name}",
        "station_name": f"Adjusted Polycam images: {main_image_name}",
        "translation": f"{translation[0]}, {translation[2]}, {translation[1]}", 
        "rotation_axis": f"{rotation_axis[0]}, {rotation_axis[2]}, {rotation_axis[1]}", 
        "rotation_angle": angle_degrees, 
    }
    #Create event
    print("Event metadata:")
    print(event_metadata)
    new_event ={
        "externalId":f"event-{main_image_name}",
        "type":"scan",
        "subtype":"terrestial",
        "description":f"Scan data for the {face} face of the cubemap.",
        "metadata":event_metadata,
        "dataSetId": dataset_id 
    }
    c.events.create([new_event])
    print(f"Uploaded image and created event for: {main_image_name}")


if __name__ == "__main__":
    #front_image_path = 'data/Feb11at7-35-PM-poly/corrected_images/408728696901.jpg'
    #json_file_path = 'data/Feb11at7-35-PM-poly/corrected_cameras/408728696901.json'
    creds, config, c = init_cognite_connect()
    dummy_images_folder = 'data/dummycubemap'
    front_image_folder = "data/Feb11at7-35-PM-poly/corrected_images"
    json_files_folder = "data/Feb11at7-35-PM-poly/corrected_cameras"
    mesh_info_path = "data/Feb11at7-35-PM-poly/mesh_info.json"
    counter = 0
    for file in os.listdir(front_image_folder):
        if file.endswith(".jpg"):
            front_image_path = os.path.join(front_image_folder, file)
            json_file_path = os.path.join(json_files_folder, file.replace(".jpg", ".json"))
            if not os.path.exists(json_file_path):
                print(f"No JSON file found for {file}, skipping...")
                continue
            print(f"Processing {front_image_path} and {json_file_path}")
            prepare_and_upload_image(c, front_image_path, json_file_path, dummy_images_folder, mesh_info_path)
        counter += 1
        if counter > 4:
            break
    print(f"{counter} images processed and uploaded to CDF.")

