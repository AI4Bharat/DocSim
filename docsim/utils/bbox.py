
from imgaug.augmentables.polys import Polygon, PolygonsOnImage

def convert_coco_to_polygons(coco_bboxes, labels, img=None):
    polygons = []
    for bbox, label in zip(coco_bboxes, labels):
        element = [[*bbox[0:2]], [bbox[0]+bbox[2], bbox[1]],
              [bbox[0], bbox[1]+bbox[3]], [bbox[0]+bbox[2], bbox[1]+bbox[3]]]
        polygons.append(Polygon(element, label=label))
    
    if img is not None:
        polygons = PolygonsOnImage(polygons, shape=img.shape)
    return polygons

def convert_polygons_to_coco(polygons):
    bboxes_list,labels_list = [], []
    for polygon in polygons:
        bboxes_list.append([*polygon[0], *(polygon[2] - polygon[0])])
        labels_list.append(polygon.label)
    return  bboxes_list, labels_list
