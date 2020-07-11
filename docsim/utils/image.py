import os
from glob import glob
import random
from PIL import Image
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

import qrcode
def get_qr_img(min_v=3, max_v=7, data=None):
    version = random.randint(min_v, max_v)
    qr = qrcode.QRCode(version=version, border=0)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

import barcode
def get_barcode(data, shape=(235, 27)):
    bar_class = barcode.get_barcode_class('code128')
    code128 = bar_class(data, barcode.writer.ImageWriter())
    code128.save('temp', options={"write_text": False, "quiet_zone": 0.5})
    with Image.open('temp.png') as img:
        bar_image = img.copy()
    os.remove('temp.png')
    resized_bar = bar_image.resize(shape, resample=Image.NEAREST)
    return resized_bar
