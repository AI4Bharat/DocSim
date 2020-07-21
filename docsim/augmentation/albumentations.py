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

    def __init__(self, main_config):
        self.shuffle = main_config.shuffle
        self.augname2groups = main_config.augname2groups
        self.setup_augmentors(main_config.augmentations)
        self.max_augmentations_per_image = main_config.max_augmentations_per_image
        
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
            aug.name, aug.p, aug.base = aug_name, aug_config['probability'], self
            
            self.augmentors.append(aug)

        return

    def augment_image(self, img, gt, completed_groups, aug_counter):
        if self.shuffle: 
            random.shuffle(self.augmentors)

        polygons = [Polygon(element['points'], element['label'])
                    for element in gt["data"]]
        polygons = PolygonsOnImage(polygons, shape=img.shape)
        bboxes, labels = convert_polygons_to_coco(polygons) 
        augmentations_done = []
        for aug in self.augmentors:
            if random.random() < aug.p and aug_counter.value < self.max_augmentations_per_image:
                if aug.name in self.augname2groups:
                    if self.augname2groups[aug.name].intersection(completed_groups):
                        continue
                    else:
                        completed_groups.update(self.augname2groups[aug.name])
                img, bboxes, labels = aug(image=img, bboxes=bboxes,
                                class_labels=labels).values()
                augmentations_done.append(aug.name)
                aug_counter.value += 1
        polygons = convert_coco_to_polygons(
            coco_bboxes=bboxes, labels=labels, img=img)
        # Put back polygons into GT
        for element, pg in zip(gt["data"], polygons):
            element['points'] = [pt.tolist() for pt in pg.exterior]
        gt["augs_done"].extend(augmentations_done)
        return img, gt
    
    @staticmethod
    def run_augment(aug, img, gt):
        polygons = [Polygon(element['points'], element['label'])
                    for element in gt]
        polygons = PolygonsOnImage(polygons, shape=img.shape)

        # TODO: Get bbxoes directly using gt instead of polygons
        bboxes, labels = convert_polygons_to_coco(polygons)
        
        img, bboxes, labels = aug(image=img, bboxes=bboxes, class_labels=labels).values()
        
        # TODO: Convert directly to GT
        polygons = convert_coco_to_polygons(
            coco_bboxes=bboxes, labels=labels, img=img).values()
        
        # Put back polygons into GT
        for element, pg in zip(gt, polygons):
            element['points'] = [pt.tolist() for pt in pg.exterior]
        
        return img, gt


def get_albu(aug, format='coco', label_fields=['class_labels']):
    return albu.Compose(aug, bbox_params=albu.BboxParams(format=format, label_fields=label_fields))
