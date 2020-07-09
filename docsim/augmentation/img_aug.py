import random
import imgaug.augmenters as iaa
from imgaug.augmentables.polys import Polygon, PolygonsOnImage
from docsim.utils.bbox import convert_coco_to_polygons, convert_polygons_to_coco
import albumentations as albu

class ImgAugAugmentor:
    
    SUPPORTED_AUGMENTATIONS = {"imgaug" : ['grayscale',
                                           'intensity_multiplier',
                                           'additive_gaussian_noise',
                                           'gaussian_blur',
                                           'quantization',
                                           'contrast',
                                           'spatter',
                                           'motion_blur',
                                           'perspective_transform',
                                           'piecewise_affine'
                                           ],
                               "albumentations": ['image_compression',
                                                  'posterize',
                                                  'blur',
                                                  'median_blur',
                                                  'iso_noise'
                                                  ]
                               }
    
    def __init__(self, config):
        self.shuffle = 'random_sequence' in config and config['random_sequence']
        self.setup_augmentors(config['augmentations'])
    
    def setup_augmentors(self, augmentations):
        self.augmentors = []
        for aug_name, aug_config in augmentations.items():
            aug = None
            if aug_name == 'grayscale':
                aug = iaa.Grayscale()
            elif aug_name == 'intensity_multiplier':
                aug = iaa.Multiply((aug_config.get('min_multiplier', 0.5), aug_config.get('min_multiplier', 1.5)))
            elif aug_name == 'additive_gaussian_noise':
                aug = VariableRangeAdditiveGaussianNoise(aug_config.get('min_scale', 0.05), aug_config.get('max_scale', 0.25))
            elif aug_name == 'gaussian_blur':
                aug = iaa.GaussianBlur(sigma=(aug_config.get('sigma_min', 0.0), aug_config.get('sigma_max', 0.0)))
            elif aug_name == 'quantization':
                aug = iaa.KMeansColorQuantization(n_colors=(aug_config.get('min_colors', 32), aug_config.get('max_colors', 64)))
            elif aug_name == 'contrast':
                aug = iaa.SigmoidContrast(
                    gain=(aug_config.get('min_gain', 6), aug_config.get('max_gain', 10)),
                    cutoff=(aug_config.get('min_cutoff', 0.2), aug_config.get('max_cutoff', 0.6)))
            elif aug_name == 'spatter':
                aug = iaa.imgcorruptlike.Spatter(severity=aug_config.get('severity', 4))
            elif aug_name == 'motion_blur':
                # TODO: Ground-truth seems to shift a bit, but imgaug does not implement it 
                aug = iaa.MotionBlur(k=aug_config.get('kernel_size', 15),
                                     angle=(aug_config.get('min_angle', -45), aug_config.get('max_angle', 45)))
            elif aug_name == 'perspective_transform':
                aug = iaa.PerspectiveTransform(scale=(aug_config.get('min_scale', 0), aug_config.get('max_scale', 0.05)))
            elif aug_name == 'piecewise_affine':
                # Note: 10X Costly
                aug = iaa.PiecewiseAffine(scale=(aug_config.get('min_scale', 0), aug_config.get('max_scale', 0.03)))
            elif aug_name == 'image_compression':
                aug = get_albu([albu.ImageCompression(quality_lower=aug_config.get('quality_lower', 90), 
                                                      quality_upper=aug_config.get('quality_upper'), 
                                                      p=aug_config.get('probabilty',0.5))])
            elif aug_name == 'posterize':
                aug = get_albu([albu.Posterize(num_bits=aug_config.get('num_bits',4), p=aug_config.get('probability',0.5))])
            elif aug_name == 'blur':
                aug = get_albu([albu.Blur(blur_limit=aug_config.get('blur_limit',7), p=aug_config.get('probabilty', 0.5))])
            elif aug_name == 'median_blur':
                aug = get_albu([albu.MedianBlur(blur_limit=aug_config.get(
                    'blur_limit', 7), p=aug_config.get('probabilty', 0.5))])
            elif aug_name == 'iso_noise':
                aug = get_albu([albu.ISONoise(color_shift=(aug_config.get('min_color_shift', 0.01), aug_config.get('max_color_shift', 0.05)), 
                                              intensity=(aug_config.get('min_intensity', 0.1), aug_config.get('min_intensity', 0.5)), \
                                              p=aug_config.get('probabilty', 0.5))])
            if not aug: 
                continue
            aug.p = aug_config['probability']
            self.augmentors.append(aug)
        
        return
    
    def augment_image(self, img, gt):
        if self.shuffle: # TODO: Move to top-level augmentor?
            random.shuffle(self.augmentors)
        
        polygons = [Polygon(element['points'], element['label']) for element in gt]
        polygons = PolygonsOnImage(polygons, shape=img.shape)
        
        for aug in self.augmentors:
            if random.random() < aug.p:
                #TODO: Handle it better
                if "imgaug" in str(type(aug)) or "docsim" in str(type(aug)):
                    img, polygons = aug(image=img, polygons=polygons)
                elif "albumentations" in str(type(aug)):
                    bboxes, labels = convert_polygons_to_coco(polygons)
                    augmented = aug(image=img, bboxes=bboxes,
                                              class_labels=labels)
                    img, bboxes, labels = augmented.values()
                    polygons = convert_coco_to_polygons(
                        coco_bboxes = bboxes, labels=labels, img=img)
                else:
                    raise NotImplementedError
                
        # Put back polygons into GT
        for element, pg in zip(gt, polygons):
            polygon = [pt.tolist() for pt in pg.exterior]
            element['points'] = polygon

        return img, gt
        

class VariableRangeAdditiveGaussianNoise:
    def __init__(self, min_scale, max_scale):
        self.min_upper_scale = min_scale*255.0
        self.max_upper_scale = max_scale*255.0
        self.upper_range = self.max_upper_scale - self.min_upper_scale
    
    def __call__(self, image, polygons):
        upper_scale = (random.random() * self.upper_range) + self.min_upper_scale
        aug = iaa.AdditiveGaussianNoise(scale=(0, upper_scale))
        return aug(image=image), polygons

def get_albu(aug, format='coco', label_fields=['class_labels']):
    return albu.Compose(aug, bbox_params=albu.BboxParams(format=format, label_fields=label_fields))
