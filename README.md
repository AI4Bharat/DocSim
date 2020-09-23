# DocSim -- Documents Simulator

Synthetically generate documents!  
[Check here](/documentation/Features.md) for list of all features

## Requirements

- Atleast Python 3.7
- `pip install -r dependencies.txt`
- Check [`documentation/Installation`](/documentation/Installation.md) for other libraries

## Example Usage

### Generate synthetic images

```
python generate.py <template.json> <num_samples> <output_folder>
```

Check the [`templates/`](templates/) folder for sample document templates.

### Augment generated images

```
python augment.py <config.json> <input_folder> <num_epochs> <output_folder> <num_workers>
```

Check [`documentation/Augmentation`](documentation/Augmentation.md) for more details.
