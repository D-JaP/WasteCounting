from PIL import Image, ImageDraw
from os.path import join

# Loop through list of image -> and rotate, also fix json file
root = './'
# root_data is where you download the FDST dataset
root_data = '../data/image/'
original = '../data/temp/'

# Load the image
image = Image.open(join(root_data,"023.jpg"))

# Create a drawing object
draw = ImageDraw.Draw(image)

# Define the coordinates of the bounding box
top = 1594
left = 2893
height = 86
width = 104

# Draw the bounding box on the image
draw.rectangle([left, top, left + width, top + height], outline='red', width=5)

# Save or display the image with the bounding box
image.save('image_with_bbox_new.jpg')



