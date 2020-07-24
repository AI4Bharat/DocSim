import os
import sys
from glob import glob
from tqdm import tqdm
import json
import random
import cv2
import numpy as np
from imageio import imread, imsave
from joblib import Parallel, delayed

from docsim.augmentation.img_aug import ImgAugAugmentor
from docsim.augmentation.ocr_deg import OCRoDegAugmentor
from docsim.augmentation.albumentations import Albumentor
from docsim.augmentation.custom_augs import CustomAugmentations

from docsim.utils.image import get_all_images

  
class Augmentor:

    SUPPORTED_AUGMENTATIONS = ImgAugAugmentor.SUPPORTED_AUGMENTATIONS + \
        OCRoDegAugmentor.SUPPORTED_AUGMENTATIONS + \
        Albumentor.SUPPORTED_AUGMENTATIONS + CustomAugmentations.SUPPORTED_AUGMENTATIONS

    class AugmentCounter:
        def __init__(self, value):
            self.value = value
            
    def __init__(self, config_json):
        with open(config_json, encoding='utf-8') as f:
            config = json.load(f)
        self.setup_defaults(config)
        # TODO: Fix the impurity below
        augmentors = [ImgAugAugmentor(self), OCRoDegAugmentor(
            self), Albumentor(self), CustomAugmentations(self)]
        self.augmentors = [a for a in augmentors if a.augmentors]
                
    def setup_defaults(self, config):
        self.config = config
        self.debug = config['debug'] if 'debug' in config else False  
        self.augmentations = config['augmentations']
        self.shuffle = 'random_sequence' in config and config['random_sequence']
        self.max_augmentations_per_image = config['max_augmentations_per_image']
        for aug_name, aug_config in self.augmentations.items():
            if aug_name not in Augmentor.SUPPORTED_AUGMENTATIONS:
                print('No augmentor for:', aug_name)
                continue
            if 'probability' not in aug_config:
                aug_config['probability'] = 0.5

        self.augname2groups = {}
        if 'mutually_exclusive_augmentations' in config:
            for group_id, one_of_group in enumerate(config['mutually_exclusive_augmentations']):
                for aug_name in one_of_group:
                    if aug_name not in self.augname2groups:
                        self.augname2groups[aug_name] = set()
                    self.augname2groups[aug_name].add(group_id)

        return

    def get_image_with_bboxes(self, img, gt, BOX_COLOR=(255, 0, 0), thickness=2):
        img = img.copy()
        bboxes = [i["points"] for i in gt]
        for bbox in bboxes:
            bbox = np.array(bbox, np.int32).reshape((-1, 1, 2))
            img = cv2.polylines(
                img, [bbox], color=BOX_COLOR, isClosed=True, thickness=thickness)
            
        return img
        
    def augment_epoch(self, image, output_path_prefix):
        gt_file = os.path.splitext(image)[0] + '.json'
        if not os.path.isfile(gt_file):
            print('No GT for:', image)
            return

        # Read image and GT
        img = imread(image)[:, :, :3]
        with open(gt_file, encoding='utf-8') as f:
            gt = json.load(f)
            
        # To keep track of augmentations done
        gt["augs_done"] = []
        aug_counter = Augmentor.AugmentCounter(0)
        
        # Augment!
        if self.shuffle:
            random.shuffle(self.augmentors)
        completed_groups = set()
        for augmentor in self.augmentors:
            img, gt = augmentor.augment_image(img, gt, completed_groups, aug_counter)

        if self.debug:
            img = self.get_image_with_bboxes(img, gt["data"])
        # Save augmented output
        out_img_file = output_path_prefix + os.path.basename(image)
        imsave(out_img_file, img)
        out_gt_file = output_path_prefix + os.path.basename(gt_file)
        with open(out_gt_file, 'w', encoding='utf-8') as f:
            json.dump(gt, f, ensure_ascii=False, indent=4)
        return

    def __call__(self, input_folder, epochs=1, output_folder=None, num_workers=1):
        if not output_folder:
            output_folder = os.path.join(input_folder, 'augmented')
        os.makedirs(output_folder, exist_ok=True)

        images = get_all_images(input_folder)
        if not images:
            exit('No images found in:', input_folder)

        for e in range(epochs):
            output_path_prefix = os.path.join(output_folder,str(e+1)+'-')
            processor = Parallel(n_jobs=num_workers, backend="multiprocessing")
            processor(delayed(self.augment_epoch)(image, output_path_prefix)
                                                                    for image in tqdm(images))
        return


if __name__ == '__main__':
    config_json, input_folder = sys.argv[1:3]
    epochs = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    output_folder = sys.argv[4] if len(sys.argv) > 4 else None
    num_workers = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    
    a = Augmentor(config_json)
    a(input_folder, epochs, output_folder, num_workers)
