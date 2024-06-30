import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def visualize_depth_maps(image_paths):
    # Set up the plot with 1 row and as many columns as there are images
    fig, axes = plt.subplots(1, len(image_paths), figsize=(20, 4))
    
    for i, image_path in enumerate(image_paths):
        # Load the depth map image
        depth_map = Image.open(image_path)
        
        # Ensure the depth map is 16-bit single-channel image
        if depth_map.mode != 'I':
            raise ValueError(f"Depth map in {image_path} must be a 16-bit single-channel image.")

        # Rotate the image by 90 degrees to the right (clockwise)
        depth_map_rotated = depth_map.rotate(-90, expand=True)

        # Convert the rotated depth map to an array
        depth_array = np.array(depth_map_rotated)

        # Convert depth from millimeters to meters for better readability
        depth_in_meters = depth_array / 1000.0

        # Display the depth map in the corresponding subplot
        ax = axes[i]
        im = ax.imshow(depth_in_meters, cmap='plasma')
        ax.set_title(f'Image {i+1}')
        ax.axis('off')  # Turn off axis labels and ticks

    # Add a colorbar to the last subplot
    fig.colorbar(im, ax=axes.ravel().tolist(), label='Depth in meters')

    plt.tight_layout()
    plt.show()

# Example usage:
# Replace these paths with the paths to your actual depth map images
image_paths = [
    "data/Feb11at7-35 PM-poly/depth/408728696901.png",
    'data/Feb11at7-35 PM-poly/depth/408730230783.png',
    'data/Feb11at7-35 PM-poly/depth/408730897688.png',
    'data/Feb11at7-35 PM-poly/depth/408731631284.png',
    'data/Feb11at7-35 PM-poly/depth/408732331534.png'
]

visualize_depth_maps(image_paths)
