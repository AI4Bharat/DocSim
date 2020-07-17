# DocSim -- Documents Simulator

Synthetically generate documents!  
[Check here](/documentation/Features.md) for list of all features

## Requirements

- Atleast Python 3.7
- `pip install -r dependencies.txt`
- Check [`documentation/Installation`](/documentation/Installation.md) for other libraries

## Instructions

### Generate synthetic images

```
python docsim\generator.py <template.json> <num_samples> <output_folder>
```

Check the [`docs/`](docs/) folder for sample documents.

### Augment generated images

```
python docsim\augmentor.py <config.json> <input_folder> <num_epochs> <output_folder>
```

Check [`documentation/Augmentation.md`](documentation/Augmentation.md) for more details.
