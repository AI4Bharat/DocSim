import os
from glob import glob
import numpy as np
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']

def get_all_images(folder):
    files = glob(os.path.join(folder, '*'))
    images = []
    for extension in IMAGE_EXTENSIONS:
        images += [file for file in files if file.lower().endswith(extension)]
    return images

def rgb2gray(rgb):
    if len(rgb.shape) == 2: return rgb
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
