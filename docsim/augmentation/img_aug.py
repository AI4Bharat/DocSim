import random
import imgaug.augmenters as iaa
from imgaug.augmentables.polys import Polygon, PolygonsOnImage


class ImgAugAugmentor:

    SUPPORTED_AUGMENTATIONS = ['grayscale',
                               'intensity_multiplier',
                               'additive_gaussian_noise',
                               'gaussian_blur',
                               'defocus',
                               'fog',
                               'quantization',
                               'contrast',
                               'spatter',
                               'motion_blur',
                               'perspective_transform',
                               'elastic_transform',
                               'piecewise_affine']

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
                aug = iaa.Multiply(
                    (aug_config.get('min_multiplier', 0.5), aug_config.get('min_multiplier', 1.5)))
            elif aug_name == 'additive_gaussian_noise':
                aug = VariableRangeAdditiveGaussianNoise(aug_config.get(
                    'min_scale', 0.05), aug_config.get('max_scale', 0.25))
            elif aug_name == 'gaussian_blur':
                aug = iaa.GaussianBlur(sigma=(aug_config.get('sigma_min', 0.0), aug_config.get('sigma_max', 0.0)))
            elif aug_name == 'defocus':
                aug = iaa.imgcorruptlike.DefocusBlur(severity=(aug_config.get('min_severity', 1), aug_config.get('min_severity', 3)))
            elif aug_name == 'fog':
                aug = iaa.imgcorruptlike.Fog(severity=(aug_config.get('min_severity', 1), aug_config.get('min_severity', 3)))
            elif aug_name == 'quantization':
                aug = iaa.KMeansColorQuantization(n_colors=(aug_config.get(
                    'min_colors', 32), aug_config.get('max_colors', 64)))
            elif aug_name == 'contrast':
                aug = iaa.SigmoidContrast(
                    gain=(aug_config.get('min_gain', 6),
                          aug_config.get('max_gain', 10)),
                    cutoff=(aug_config.get('min_cutoff', 0.2), aug_config.get('max_cutoff', 0.6)))
            elif aug_name == 'spatter':
                aug = aug = iaa.imgcorruptlike.Spatter(
                    severity=aug_config.get('severity', 4))
            elif aug_name == 'motion_blur':
                # Note: Ground-truth seems to shift a bit, but imgaug does not implement it 
                aug = iaa.MotionBlur(k=aug_config.get('kernel_size', 15),
                                     angle=(aug_config.get('min_angle', -45), aug_config.get('max_angle', 45)))
            elif aug_name == 'perspective_transform':
                aug = iaa.PerspectiveTransform(scale=(aug_config.get('min_scale', 0), aug_config.get('max_scale', 0.05)))
            elif aug_name == 'elastic_transform':
                # Note: Ground-truth seems to shift a bit, but imgaug does not implement it
                aug = ElasticTransformCorruption(severity=(aug_config.get('min_severity', 1), aug_config.get('min_severity', 3)))
            elif aug_name == 'piecewise_affine':
                # Note: 10X Costly
                aug = iaa.PiecewiseAffine(scale=(aug_config.get(
                    'min_scale', 0), aug_config.get('max_scale', 0.03)))

            if not aug:
                continue
            aug.p = aug_config['probability']
            self.augmentors.append(aug)

        return

    def augment_image(self, img, gt):
        if self.shuffle:  # TODO: Move to top-level augmentor?
            random.shuffle(self.augmentors)

        polygons = [Polygon(element['points'], element['label'])
                    for element in gt]
        polygons = PolygonsOnImage(polygons, shape=img.shape)
        for aug in self.augmentors:
            if random.random() < aug.p:
                img, polygons = aug(image=img, polygons=polygons)

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
    
    def __call__(self, image, polygons=None):
        upper_scale = (random.random() * self.upper_range) + self.min_upper_scale
        aug = iaa.AdditiveGaussianNoise(scale=(0, upper_scale))
        return aug(image=image), polygons

class ElasticTransformCorruption:
    def __init__(self, severity=2):
        self.aug = iaa.imgcorruptlike.ElasticTransform(severity)
    
    def __call__(self, image, polygons=None):
        return self.aug(image=image), polygons
