# Augmentations relevant to textual images

Check [`/docs/sample_augmentation/config.json`](/docs/sample_augmentation/config.json) for a sample configuration file for augmentation.

## Supported Augmentations

### Library: [`imgaug`](https://github.com/aleju/imgaug#example-images)

|Augmentation|Description|
|------------|-----------|
|[`grayscale`](https://imgaug.readthedocs.io/en/latest/source/overview/color.html#grayscale)|Black-and-White Augmentation|
|[`intensity_multiplier`](https://imgaug.readthedocs.io/en/latest/source/overview/arithmetic.html#multiply)|Intensity Augmentation (Lighting)|
|[`additive_gaussian_noise`](https://imgaug.readthedocs.io/en/latest/source/overview/arithmetic.html#additivegaussiannoise)|Adds Gaussian Noise (Salt-and-pepper if black-and-white is passed)|
|[`defocus`](https://imgaug.readthedocs.io/en/latest/source/overview/imgcorruptlike.html#defocusblur)|Image Blurring because of defocused image|
|[`fog`](https://imgaug.readthedocs.io/en/latest/source/overview/imgcorruptlike.html#fog)|Simulates sparse shadows|
|[`quantization`](https://imgaug.readthedocs.io/en/latest/source/overview/color.html#kmeanscolorquantization)|Simulates camera's color depth variations as in low-end cameras|
|[`contrast`](https://imgaug.readthedocs.io/en/latest/source/overview/contrast.html#sigmoidcontrast)|Simulates contrast variations as in badly calibrated cameras|
|[`spatter`](https://imgaug.readthedocs.io/en/latest/source/overview/imgcorruptlike.html#spatter)|Simulates dirty documents (severity: 4-5)|
|[`motion_blur`](https://imgaug.readthedocs.io/en/latest/source/overview/blur.html#motionblur)|Simulates camera shakes when capturing|
|[`perspective_transform`](https://imgaug.readthedocs.io/en/latest/source/overview/geometric.html#perspectivetransform)|Simulate the different perspectives/angles from which one can capture a photo|
|[`elastic_transform`](https://github.com/bethgelab/imagecorruptions#imagecorruptions)|Simulates disorientations of printed text at the character-level|
|[`piecewise_affine`](https://imgaug.readthedocs.io/en/latest/source/overview/geometric.html#piecewiseaffine)|Simulates expanded/contracted papers depressed at a location

### Library: [`ocrodeg`](https://github.com/NVlabs/ocrodeg) - Scanned Images Augmentor

|Augmentation|Description|
|------------|-----------|
|[`gaussian_warp`](https://github.com/NVlabs/ocrodeg#random-distortions)|Local Warping to simulate ink spread & paper curls|
|[`1d_surface_distort`](https://github.com/NVlabs/ocrodeg#ruled-surface-distortions)|Simulates vertically rolled and stretched paper|
|[`binarized_blur`](https://github.com/NVlabs/ocrodeg#blur-thresholding-noise)|Thresholding + GaussianBlur|
|[`blotches`](https://github.com/NVlabs/ocrodeg#random-blobs)|Patches of black-and-white simulating printing ink scatters|
|[`multiscale_black_noise`](https://github.com/NVlabs/ocrodeg#foreground--background-selection)|Simulates very old paper background|
|[`fibrous_noise`](https://github.com/NVlabs/ocrodeg#fibrous-noise)|Add a fiber background and topple some noise

### Other augmentations

|Augmentation|Description|
|------------|-----------|
|[`creases_and_curls`](https://stackoverflow.com/questions/53907633/)|Simulate folds and curls of a paper|

<hr/>

## Footnotes

### Other similar libraries that didn't help

* https://github.com/mdbloice/Augmentor (Only segmentation supported)
* https://github.com/bethgelab/imagecorruptions (Subset of imgaug)
* [github.com/UjjwalSaxena/Automold--Road-Augmentation-Library](https://github.com/UjjwalSaxena/Automold--Road-Augmentation-Library) (not much relevant)
* [github.com/Paperspace/DataAugmentationForObjectDetection](https://github.com/Paperspace/DataAugmentationForObjectDetection) (Subset of imgaug)
* https://github.com/mahmoudnafifi/WB_color_augmenter (Not relevant for text)
* https://github.com/codebox/image_augmentor (Subset of imgaug)
* https://github.com/mastnk/imagedegrade (Subset of imgaug)