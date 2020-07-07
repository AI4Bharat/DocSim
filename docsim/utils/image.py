import os
from glob import glob
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']

def get_all_images(folder):
    files = glob(os.path.join(folder, '*'))
    images = []
    for extension in IMAGE_EXTENSIONS:
        images += [file for file in files if file.lower().endswith(extension)]
    return images
