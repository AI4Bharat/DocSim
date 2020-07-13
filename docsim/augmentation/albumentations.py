import albumentations as albu
import random
from imgaug.augmentables.polys import Polygon, PolygonsOnImage
from docsim.utils.bbox import convert_coco_to_polygons, convert_polygons_to_coco

class Albumentor:
    SUPPORTED_AUGMENTATIONS = [
        'image_compression',
        'posterize',
        'blur',
        'median_blur',
        'iso_noise'
    ]

    def __init__(self, config):
        self.shuffle = 'random_sequence' in config and config['random_sequence']
        self.setup_augmentors(config['augmentations'])

    def setup_augmentors(self, augmentations):
        self.augmentors = []
        for aug_name, aug_config in augmentations.items():
            aug = None
            if aug_name == 'image_compression':
                aug = get_albu([albu.ImageCompression(quality_lower=aug_config.get('quality_lower', 90),
                                                      quality_upper=aug_config.get(
                                                          'quality_upper'),
                                                      p=aug_config.get('probabilty', 0.5))])
            elif aug_name == 'posterize':
                aug = get_albu([albu.Posterize(num_bits=aug_config.get(
                    'num_bits', 4), p=aug_config.get('probability', 0.5))])
            elif aug_name == 'blur':
                aug = get_albu([albu.Blur(blur_limit=aug_config.get(
                    'blur_limit', 7), p=aug_config.get('probabilty', 0.5))])
            elif aug_name == 'median_blur':
                aug = get_albu([albu.MedianBlur(blur_limit=aug_config.get(
                    'blur_limit', 7), p=aug_config.get('probabilty', 0.5))])
            elif aug_name == 'iso_noise':
                aug = get_albu([albu.ISONoise(color_shift=(aug_config.get('min_color_shift', 0.01), aug_config.get('max_color_shift', 0.05)),
                                              intensity=(aug_config.get('min_intensity', 0.1), aug_config.get(
                                                  'min_intensity', 0.5)),
                                              p=aug_config.get('probabilty', 0.5))])
            if not aug:
                continue
            aug.p = aug_config['probability']
            self.augmentors.append(aug)

        return

    def augment_image(self, img, gt):
        if self.shuffle: 
            random.shuffle(self.augmentors)

        polygons = [Polygon(element['points'], element['label'])
                    for element in gt]
        polygons = PolygonsOnImage(polygons, shape=img.shape)

        bboxes, labels = convert_polygons_to_coco(polygons) 
        for aug in self.augmentors:
            print("aug",aug)
            if random.random() < aug.p:
                augmented = aug(image=img, bboxes=bboxes,
                                class_labels=labels)
                img, bboxes, labels = augmented.values()
                
        polygons = convert_coco_to_polygons(
            coco_bboxes=bboxes, labels=labels, img=img)
        # Put back polygons into GT
        for element, pg in zip(gt, polygons):
            polygon = [pt.tolist() for pt in pg.exterior]
            element['points'] = polygon

        return img, gt


def get_albu(aug, format='coco', label_fields=['class_labels']):
    return albu.Compose(aug, bbox_params=albu.BboxParams(format=format, label_fields=label_fields))
