from PIL import Image
import os
import random
from random import randrange
import requests
import io

from docsim.utils.random import random_string
from docsim.utils.image import *

class ImageRetriever:
    def __init__(self, img_path, dims):
        size = (dims['width'], dims['height'])
        self.image = Image.open(img_path).resize(size)
        self.path = img_path
        
    def generate(self):
        return self.image, self.path

class ImageGenerator:
    def __init__(self, img_folder, dims):
        self.img_size = (dims['width'], dims['height'])
        self.images = get_all_images(img_folder)
        
        if not self.images:
            exit('No images found in %s' % img_folder)
    
    def generate(self):
        img_index = randrange(len(self.images))
        img_path = self.images[img_index]
        img = Image.open(img_path).resize(self.img_size)
        return img, img_path

class OnlineFaceGenerator:
    URL = 'https://thispersondoesnotexist.com/image'
    def __init__(self, dims):
        self.img_size = (dims['width'], dims['height']) if dims else (400, 400)
    
    def generate(self):
        return self.random_face().resize(self.img_size), None
        
    def random_face(self):
        r = requests.get(OnlineFaceGenerator.URL).content
        return Image.open(io.BytesIO(r))

import qrcode
class QRCodeGenerator:
    def __init__(self, details):
        if 'string_len_min' not in details:
            details['string_len_min'] = 7
        if 'string_len_max' not in details:
            details['string_len_max'] = 15
        if 'version_min' not in details:
            details['version_min'] = 3
        if 'version_max' not in details:
            details['version_max'] = 7

        self.details = details
        self.img_size = (details['dims']['width'], details['dims']['height']) if 'dims' in details else (400, 400)
    
    def get_data(self):
        if 'data_source' in self.details:
            return self.details['data_source']['last_generated']
        else:
            return random_string(self.details['string_len_min'], self.details['string_len_max'])
        
    def generate(self):
        string = self.get_data()
        version = random.randint(self.details['version_min'], self.details['version_max'])
        qr = qrcode.QRCode(version=version, border=0)
        qr.add_data(string)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img.resize(self.img_size), string

import barcode
class BarCodeGenerator:
    def __init__(self, details):
        if 'string_len_min' not in details:
            details['string_len_min'] = 7
        if 'string_len_max' not in details:
            details['string_len_max'] = 15
        self.details = details
        self.img_size = (details['dims']['width'], details['dims']['height']) if 'dims' in details else (235, 27)
    
    def get_data(self):
        if 'data_source' in self.details:
            return self.details['data_source']['last_generated']
        else:
            return random_string(self.details['string_len_min'], self.details['string_len_max'])
    
    def generate(self):
        data = self.get_data()
        bar_class = barcode.get_barcode_class('code128')
        code128 = bar_class(data, barcode.writer.ImageWriter())
        code128.save('temp', options={"write_text": False, "quiet_zone": 0.5})
        with Image.open('temp.png') as img:
            bar_image = img.copy()
        os.remove('temp.png')
        resized_bar = bar_image.resize(self.img_size, resample=Image.NEAREST)
        return resized_bar, data
