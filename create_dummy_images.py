from PIL import Image, ImageDraw, ImageFont

# Define image size and text settings
size = (768, 768)
text_position = (184, 334)
font = font = ImageFont.load_default()


# Define the colors and texts for each image
configs = {
    'top.jpg': ('red', 'TOP'),
    'bottom.jpg': ('purple', 'BOTTOM'),
    'left.jpg': ('orange', 'LEFT'),
    'right.jpg': ('black', 'RIGHT')
}

for filename, (bg_color, text) in configs.items():
    # Create a new image with the specified background color
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)

    # Calculate text position to be centered
    def textsize(text, font):
        im = Image.new(mode="P", size=(0, 0))
        draw = ImageDraw.Draw(im)
        _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
        return width, height
    text_width, text_height = textsize(text, font)

    text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)

    # Choose text color based on background for visibility
    text_color = 'white' if bg_color == 'black' else 'black'

    # Add text to the image
    draw.text(text_position, text, fill=text_color, font=font)

    # Save the image
    img.save(filename)
