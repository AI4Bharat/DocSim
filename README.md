# DocSim -- Documents Simulator

Synthetically generate random text documents!  
[Check here](/documentation/Features.md) for list of all features

## Demo

|Template|Generated|Augmented|
|:------:|:-------:|:-------:|
|<img src="documentation/demo/template.jpg"/>|<img src="documentation/demo/generated.jpg"/>|<img src="documentation/demo/augmented.jpg"/>|

## Requirements

- Atleast Python 3.7
- `pip install -r dependencies.txt`
- Check [`documentation/Installation`](/documentation/Installation.md) for further instructions

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

<hr/>

## Footnotes

For any problems or queries, please report under the "Issues" tab.  
Feel free to contribute by sending a Pull Request.

### Other similar libraries

- [DocCreator](https://doc-creator.labri.fr/)
- [DocEmul](https://github.com/narVidhai/DocEmul)
