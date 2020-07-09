import os, sys
from glob import glob
from tqdm import tqdm
import json
import random
from imageio import imread, imsave

from docsim.augmentation.img_aug import ImgAugAugmentor
from docsim.augmentation.ocr_deg import OCRoDegAugmentor
from docsim.augmentation.albumentations import Albumentor

from docsim.utils.image import get_all_images

class Augmentor:
    
    SUPPORTED_AUGMENTATIONS = ImgAugAugmentor.SUPPORTED_AUGMENTATIONS + \
        OCRoDegAugmentor.SUPPORTED_AUGMENTATIONS + Albumentor.SUPPORTED_AUGMENTATIONS
    
    def __init__(self, config_json):
        with open(config_json, encoding='utf-8') as f:
            config = json.load(f)
        self.augmentations = config['augmentations']
        self.shuffle = 'random_sequence' in config and config['random_sequence']
        self.setup_defaults()
        augmentors = [ImgAugAugmentor(config), OCRoDegAugmentor(config), Albumentor(config)]
        self.augmentors = [a for a in augmentors if a.augmentors]
         
    def setup_defaults(self):
        for aug_name, aug_config in self.augmentations.items():
            if aug_name not in Augmentor.SUPPORTED_AUGMENTATIONS:
                print('No augmentor for:', aug_name)
                continue
            if 'probability' not in aug_config:
                aug_config['probability'] = 0.5
            
        return
    
    def augment(self, images, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        for image in tqdm(images):
            gt_file = os.path.splitext(image)[0] + '.json'
            if not os.path.isfile(gt_file):
                print('No GT for:', image)
                continue
            
            # Read image and GT
            img = imread(image)[:, :, :3]
            with open(gt_file, encoding='utf-8') as f:
                gt = json.load(f)
            
            # Augment!
            if self.shuffle:
                random.shuffle(self.augmentors)
            for augmentor in self.augmentors:
                img, gt = augmentor.augment_image(img, gt)
            
            # Save augmented output
            out_img_file = os.path.join(output_folder, os.path.basename(image))
            imsave(out_img_file, img)
            out_gt_file = os.path.join(output_folder, os.path.basename(gt_file))
            with open(out_gt_file, 'w', encoding='utf-8') as f:
                json.dump(gt, f, ensure_ascii=False, indent=4)
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
