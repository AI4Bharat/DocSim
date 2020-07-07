# DocSim -- Documents Simulator

Synthetically generate documents!

## Requirements

- Atleast Python 3.7
- `pip install -r dependencies.txt`
- Place your fonts in the `fonts\` folder

## Features

- JSON template-based synthetic images and ground-truth generation
- Support for filling using multiple-languages
- Transliteration-based parallel multi-lingual parallel text
- Support for QR and Bar code generation

## Instructions

### Generate synthetic images

```
python docsim\generator.py <template.json> <num_samples> <output_folder>
```

### Augment generated images

```
python docsim\augmentor.py <config.json> <input_folder> <num_epochs> <output_folder>
```
