import os, sys
import random
from glob import glob
from tqdm import tqdm
import json
from imageio import imread, imsave
import imgaug.augmenters as iaa

from docsim.augmentation.img_aug import *
from docsim.utils.image import get_all_images

class Augmentor:
    SUPPORTED_AUGMENTATIONS = ['grayscale', 'intensity_multiplier', 'additive_gaussian_noise']
    def __init__(self, config_json):
        with open(config_json, encoding='utf-8') as f:
            config = json.load(f)
        self.augmentations = config['augmentations']
        self.shuffle = 'random_sequence' in config and config['random_sequence']
        self.setup_defaults()
        self.setup_basic_augmentors()
        
    def setup_defaults(self):
        for aug_name, aug_config in self.augmentations.items():
            if aug_name not in Augmentor.SUPPORTED_AUGMENTATIONS:
                print('No augmentor for:', aug_name)
                continue
            if 'probability' not in aug_config:
                aug_config['probability'] = 0.5
            
        return
    
    def setup_basic_augmentors(self):
        self.basic_augmentors = []
        for aug_name, aug_config in self.augmentations.items():
            aug = None
            if aug_name == 'grayscale':
                aug = iaa.Grayscale()
            elif aug_name == 'intensity_multiplier':
                aug = iaa.Multiply((aug_config.get('min_multiplier', 0.5), aug_config.get('min_multiplier', 1.5)))
            elif aug_name == 'additive_gaussian_noise':
                aug = VariableRangeAdditiveGaussianNoise(aug_config.get('min_scale', 0.05), aug_config.get('max_scale', 0.25))
            
            if not aug:
                continue
            aug.p = aug_config['probability']
            self.basic_augmentors.append(aug)
        
        return
    
    def augment_image(self, img):
        if self.shuffle:
            random.shuffle(self.basic_augmentors)
        
        for aug in self.basic_augmentors:
            if random.random() < aug.p:
                img = aug(image=img)
        
        return img
    
    def augment(self, images, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        for image in tqdm(images):
            img = imread(image)[:, :, :3]
            img = self.augment_image(img)
            output = os.path.join(output_folder, os.path.basename(image))
            imsave(output, img)
        return
    
    def __call__(self, input_folder, epochs=1, output_folder=None):
        if not output_folder:
            output_folder = os.path.join(input_folder, 'augmented')
        os.makedirs(output_folder, exist_ok=True)
        
        images = get_all_images(input_folder)
        if not images:
            exit('No images found in:', input_folder)
        
        for e in range(epochs):
            self.augment(images, os.path.join(output_folder, str(e+1)))
        
        return
    
if __name__ == '__main__':
    config_json, input_folder = sys.argv[1:3]
    epochs = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    output_folder = sys.argv[4] if len(sys.argv) > 4 else None
    
    a = Augmentor(config_json)
    a(input_folder, epochs, output_folder)
