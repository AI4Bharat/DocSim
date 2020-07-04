import barcode
from barcode.writer import ImageWriter
import PIL
from PIL import Image
import os

def get_barcode(data, shape=(235, 27)):
    bar_class = barcode.get_barcode_class('code128')
    writer=ImageWriter()
    code128 = bar_class(data, writer)
    code128.save('temp', options={"write_text": False, "quiet_zone": 0.5})
    bar_image = Image.open('temp.png')
    os.remove('temp.png')
    resized_bar = bar_image.resize(shape, resample=PIL.Image.NEAREST)
    return resized_bar
