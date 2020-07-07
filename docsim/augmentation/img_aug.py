import random
import imgaug.augmenters as iaa

## Basic Augmentations

class VariableRangeAdditiveGaussianNoise:
    def __init__(self, min_scale, max_scale):
        self.min_upper_scale = min_scale*255.0
        self.max_upper_scale = max_scale*255.0
        self.upper_range = self.max_upper_scale - self.min_upper_scale
    
    def __call__(self, image):
        upper_scale = (random.random() * self.upper_range) + self.min_upper_scale
        aug = iaa.AdditiveGaussianNoise(scale=(0, upper_scale))
        return aug(image=image)
