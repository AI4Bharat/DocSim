import ocrodeg
import random
import numpy as np
from docsim.utils.image import rgb2gray

class OCRoDegAugmentor:
    
    SUPPORTED_AUGMENTATIONS = [
        'gaussian_warp',
        '1d_surface_distort',
        'binarized_blur',
        'blotches',
        'multiscale_black_noise',
        'fibrous_noise'
    ]
    
    def __init__(self, config):
        self.shuffle = 'random_sequence' in config and config['random_sequence']
        self.setup_augmentors(config['augmentations'])
    
    def setup_augmentors(self, augmentations):
        self.augmentors = []
        for aug_name, aug_config in augmentations.items():
            aug = None
            if aug_name == 'gaussian_warp':
                aug = GaussianWarp(
                    sigma=(aug_config.get('min_sigma', 0.2), aug_config.get('max_sigma', 0.5)),
                    maxdelta=(aug_config.get('min_delta', 4.0), aug_config.get('max_sigma', 6.0)))
            elif aug_name == '1d_surface_distort':
                aug = RuledSurface1dDistort(
                    magnitude=(aug_config.get('min_magnitude', 20.0), aug_config.get('max_magnitude', 40.0)))
            elif aug_name == 'binarized_blur':
                aug = BinarizedBlur(
                    sigma=(aug_config.get('min_sigma', 0.2), aug_config.get('max_sigma', 2.0)))
            elif aug_name == 'blotches':
                aug = RandomBlotches(
                    fgblobs=(aug_config.get('min_fgblobs', 0.005), aug_config.get('max_fgblobs', 0.0005)),
                    bgblobs=(aug_config.get('min_bgblobs', 0.005), aug_config.get('max_bgblobs', 0.0005)))
            elif aug_name == 'multiscale_black_noise':
                aug = MultiScaleBlackNoise(
                    blur=(aug_config.get('min_blur', 0.5), aug_config.get('max_blur', 0.5)),
                    blotches=(aug_config.get('min_blotches', 6e-6), aug_config.get('max_blotches', 2e-5)))
            elif aug_name == 'fibrous_noise':
                aug = FibrousNoise(
                    blur=(aug_config.get('min_blur', 0.5), aug_config.get('max_blur', 0.5)),
                    blotches=(aug_config.get('min_blotches', 2e-5), aug_config.get('max_blotches', 3e-5)))
            if not aug:
                continue
            aug.p = aug_config['probability']
            self.augmentors.append(aug)
        
        return
    
    def augment_image(self, img, gt):
        if self.shuffle: # TODO: Move to top-level augmentor?
            random.shuffle(self.augmentors)
        
        for aug in self.augmentors:
            if random.random() < aug.p:
                img = aug(image=img)

        return img, gt


## -------------------- Augmentors --------------------- ##

class GaussianWarp:
    def __init__(self, sigma=(1.0,5.0), maxdelta=(4.0,5.0)):
        self.sigma = sigma
        self.maxdelta = maxdelta
        self.sigma_range = sigma[1] - sigma[0]
        self.maxdelta_range = maxdelta[1] - maxdelta[0]
    
    def __call__(self, image):
        sigma = random.random() * self.sigma_range + self.sigma[0]
        maxdel = random.random() * self.maxdelta_range + self.maxdelta[0]
        noise = ocrodeg.bounded_gaussian_noise(image.shape[:2], sigma=sigma, maxdelta=maxdel)
        
        if len(image.shape) == 2:
            return ocrodeg.distort_with_noise(image, noise)
        
        for i in range(image.shape[-1]):
            image[:,:,i] = ocrodeg.distort_with_noise(image[:,:,i], noise.copy())
        
        return image

class RuledSurface1dDistort:
    def __init__(self, magnitude=(15.0, 40.0)):
        self.magnitude = magnitude
        self.magnitude_range = magnitude[1] - magnitude[0]
    
    def __call__(self, image):
        mag = random.random() * self.magnitude_range + self.magnitude[0]
        noise = ocrodeg.noise_distort1d(image.shape[:2], magnitude=mag)
        
        if len(image.shape) == 2:
            return ocrodeg.distort_with_noise(image, noise)
        
        for i in range(image.shape[-1]):
            image[:,:,i] = ocrodeg.distort_with_noise(image[:,:,i], noise.copy())
        
        return image

class BinarizedBlur:
    def __init__(self, sigma=(0.0,2.0)):
        self.sigma = sigma
        self.sigma_range = sigma[1] - sigma[0]
    
    def __call__(self, image):
        sigma = random.random() * self.sigma_range + self.sigma[0]
        
        # Image could be in uint8; normalize to [0, 1] for this function and reverse it
        image = ocrodeg.binary_blur(image/255.0, sigma)
        return (image*255.0).astype(np.uint8)

class RandomBlotches:
    def __init__(self, fgblobs=(1e-4, 3e-4), bgblobs=(1e-4, 3e-4)):
        self.fgblobs = fgblobs
        self.bgblobs = bgblobs
        
        self.fgblobs_range = fgblobs[1] - fgblobs[0]
        self.bgblobs_range = bgblobs[1] - bgblobs[0]
        
    def __call__(self, image):
        white = random.random() * self.fgblobs_range + self.fgblobs[0]
        black = random.random() * self.bgblobs_range + self.bgblobs[0]
        
        # Convert from uint8 to normalized, and then back to uint8
        image = rgb2gray(image) / 255.0
        image = ocrodeg.random_blotches(image, fgblobs=white, bgblobs=black)
        return (image*255.0).astype(np.uint8)

class RandomColoredBlotches:
    def __init__(self, fgblobs=(1e-4, 3e-4), bgblobs=(1e-4, 3e-4)):
        self.fgblobs = fgblobs
        self.bgblobs = bgblobs
        
        self.fgblobs_range = fgblobs[1] - fgblobs[0]
        self.bgblobs_range = bgblobs[1] - bgblobs[0]
        
    def __call__(self, image):
        white = random.random() * self.fgblobs_range + self.fgblobs[0]
        black = random.random() * self.bgblobs_range + self.bgblobs[0]
        
        # Convert from uint8 to normalized, and then back to uint8
        image = image / 255.0
        for i in range(image.shape):
            image[:,:,i] = ocrodeg.random_blotches(image[:,:,i], fgblobs=white, bgblobs=black)
        return (image*255.0).astype(np.uint8)

class MultiScaleBlackNoise:
    def __init__(self, blur=(0.5,1.0), blotches=(1e-4, 3e-4)):
        self.blur = blur
        self.blotches = blotches
        
        self.blur_range = blur[1] - blur[0]
        self.blotches_range = blotches[1] - blotches[0]
    
    def __call__(self, image):
        blur = random.random() * self.blur_range + self.blur[0]
        bgblobs = random.random() * self.blotches_range + self.blotches[0]
        
        # Convert from uint8 to normalized, and then back to uint8
        image = rgb2gray(image) / 255.0
        image = ocrodeg.printlike_multiscale(image, blur=blur, blotches=bgblobs)
        return (image*255.0).astype(np.uint8)

class FibrousNoise:
    def __init__(self, blur=(0.5,1.0), blotches=(1e-4, 3e-4)):
        self.blur = blur
        self.blotches = blotches
        
        self.blur_range = blur[1] - blur[0]
        self.blotches_range = blotches[1] - blotches[0]
    
    def __call__(self, image):
        blur = random.random() * self.blur_range + self.blur[0]
        bgblobs = random.random() * self.blotches_range + self.blotches[0]
        
        # Convert from uint8 to normalized, and then back to uint8
        image = rgb2gray(image) / 255.0
        image = ocrodeg.printlike_fibrous(image, blur=blur, blotches=bgblobs)
        return (image*255.0).astype(np.uint8)
