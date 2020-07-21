import numpy as np
import cv2
from PIL import Image
import random
import math

class CustomAugmentations:
    SUPPORTED_AUGMENTATIONS = [
        'creases_and_curls',
    ]
    def __init__(self, main_config):
        self.shuffle = main_config.shuffle
        self.augname2groups = main_config.augname2groups
        self.setup_augmentors(main_config.augmentations)
        self.max_augmentations_per_image = main_config.max_augmentations_per_image
        
    def setup_augmentors(self, augmentations):
        self.augmentors = []
        aug = None
        for aug_name, aug_config in augmentations.items():
            aug = None
            if aug_name == 'creases_and_curls':
                aug = CreasesAndCurls(num_deform_rounds=2)
        
            if not aug:
                continue
            
            aug.name, aug.p, aug.base = aug_name, aug_config['probability'], self
            self.augmentors.append(aug)
        return 
    
    def augment_image(self, img, gt, completed_groups, aug_counter):
        if self.shuffle: 
            random.shuffle(self.augmentors)

        bboxes = [(element['points']) for element in gt["data"]]
        augmentations_done = []
        for aug in self.augmentors:
            if random.random() < aug.p and aug_counter.value < self.max_augmentations_per_image:
                if aug.name in self.augname2groups:
                    if self.augname2groups[aug.name].intersection(completed_groups):
                        continue
                    else:
                        completed_groups.update(self.augname2groups[aug.name])
                
                img, bboxes = aug(image=img, gt=bboxes)
                augmentations_done.append(aug.name)
                aug_counter.value += 1
        
        for element, bboxes in zip(gt["data"], bboxes):
            element['points'] = bboxes
        gt["augs_done"].extend(augmentations_done)
        return img, gt
    
    
## -------------------- Augmentors --------------------- ##

class CreasesAndCurls:
    '''
    https://openaccess.thecvf.com/content_cvpr_2018/CameraReady/3349.pdf
    https://stackoverflow.com/questions/53907633/how-to-warp-an-image-using-deformed-mesh
    '''

    def __init__(self, num_deform_rounds=2, img_pad_ratio=3, folding_prob=0.3):
        self.img_pad_ratio = img_pad_ratio
        self.folding_prob = folding_prob
        self.num_deform_rounds = num_deform_rounds
    
    def __call__(self, image, gt):

        # Enlarge image
        nw, nh = image.shape[0], image.shape[1]
        dw, dh = nw//self.img_pad_ratio, nh//self.img_pad_ratio

        padded_img = cv2.copyMakeBorder(
            image, dh, dh, dw, dw, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))

        # Pad the points
        pad_bboxes = []
        for point in gt:
            pad_bboxes.append([(box[0] + dw, box[1] + dh) for box in point])

        xs, ys = self.create_grid(padded_img)

        padded_nw, padded_nh = padded_img.shape[0], padded_img.shape[1]
        xs = xs.reshape(padded_nh, padded_nw).astype(np.float32)
        ys = ys.reshape(padded_nh, padded_nw).astype(np.float32)
        dst = cv2.remap(padded_img, xs, ys, cv2.INTER_CUBIC)
        inv_xs, inv_ys = self.get_inv_coordinates(xs, ys)

        # Adjust the bouding boxes based on distortion
        adjusted_bboxes = []
        for box in pad_bboxes:
            adjusted_bboxes.append(
                [(inv_ys[int(i[0]), int(i[1])], inv_xs[int(i[0]), int(i[1])]) for i in box])

        cropped_image, cropped_bboxes = self.croput_black_portions(
            dst, adjusted_bboxes)

        return cropped_image, cropped_bboxes

    def get_random_vs(self, rows, cols):
        vertex = (random.randint(int(0.30 * rows), int(0.70 * rows)),
                  random.randint(int(0.30 * cols), int(0.70 * cols)))
        avg = (rows + cols) / 2
        degree = 0
        while not ((degree > (1 / 12) * math.pi and degree < (5 / 12) * math.pi) or
                   (degree > (7 / 12) * math.pi and degree < (11 / 12) * math.pi) or
                   (degree > (13 / 12) * math.pi and degree < (17 / 12) * math.pi) or
                   (degree > (19 / 12) * math.pi and degree < (23 / 12) * math.pi)):
            degree = random.uniform(0, 2 * math.pi)

        v = (degree, random.uniform(avg / 12, avg / 15))
        k = math.tan(v[0])

        return vertex, v, k, avg

    def shortest_distance(self, vertex_x, vertex_y, point_x, point_y, k):
        c = k * vertex_x - vertex_y
        b, a = -1 * k, 1
        d = abs(a * point_x + b * point_y + c) / math.sqrt(a * a + b * b)
        return d

    def create_grid(self, img):
        rows = img.shape[0]
        columns = img.shape[1]
        shape = img.shape
        X, Y = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]))
        ms = np.vstack([X.ravel(), Y.ravel()]).T

        def get_w(alpha, dist_xy, rows, type):
            return (alpha / (dist_xy + alpha)) if type == "line" else 1 - math.pow(dist_xy / (rows/2), alpha)

        for _ in range(self.num_deform_rounds):
            vertex, v, k, avg = self.get_random_vs(rows, columns)
            k = math.tan(v[0])

            distances = np.vectorize(self.shortest_distance)(
                vertex[0], vertex[1], ms[:, 0], ms[:, 1], k)
            curve_type = np.random.rand(1)

            if curve_type >= self.folding_prob:
                type = "line"
                alpha = avg/3
            else:
                type = "curve"
                alpha = 1.5

            weights = np.vectorize(get_w)(alpha, distances, rows, type)
            ms[:, 0] = ms[:, 0]-(v[1]*math.cos(v[0])*weights)
            ms[:, 1] = ms[:, 1]-(v[1]*math.sin(v[0])*weights)

        return ms[:, 0], ms[:, 1]

    def get_inv_coordinates(self, xs, ys):

        # TODO: Vectorize
        inv_xs, inv_ys = np.zeros(xs.shape), np.zeros(ys.shape)
        for col in range(xs.shape[0]):
            for row in range(xs.shape[1]):
                dst_x, dst_y = xs[col, row], ys[col, row]
                if dst_x < xs.shape[0] and dst_x >= 0 and dst_y < xs.shape[1] and dst_y >= 0:
                    inv_xs[int(dst_x), int(dst_y)] = col
                    inv_ys[int(dst_x), int(dst_y)] = row

        inv_xs[inv_xs == 0] = np.nan
        inv_ys[inv_ys == 0] = np.nan

        def fill_zeros_with_last(arr):
            mask = np.isnan(arr)
            idx = np.where(~mask, np.arange(mask.shape[1]), 0)
            np.maximum.accumulate(idx, axis=1, out=idx)
            out = arr[np.arange(idx.shape[0])[:, None], idx]
            return out

        inv_xs = fill_zeros_with_last(inv_xs)
        inv_ys = fill_zeros_with_last(inv_ys)

        return inv_xs, inv_ys

    def croput_black_portions(self, img, bboxes):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)>2 else img
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return img, bboxes
        cnt = contours[0]
        x, y, w, h = cv2.boundingRect(cnt)

        cropped_bboxes = []
        for point in bboxes:
            cropped_bboxes.append([(box[0] - x, box[1] - y)
                                   for box in point])
        return img[y:y+h, x:x+w], cropped_bboxes
