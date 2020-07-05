from PIL import Image
from glob import glob
from os.path import join
from random import randrange

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']

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
        files = glob(join(img_folder, '*'))
        self.images = []
        for extension in IMAGE_EXTENSIONS:
            self.images += [file for file in files if file.lower().endswith(extension)]
        
        if not self.images:
            exit('No images found in %s' % img_folder)
    
    def generate(self):
        img_index = randrange(len(self.images))
        img_path = self.images[img_index]
        img = Image.open(img_path).resize(self.img_size)
        return img, img_path
