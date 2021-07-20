# DocSim -- Documents Simulator

Synthetically generate random text documents with ground truth!  
[Check here](/documentation/Features.md) for list of all features.

Note:  
This project is only for research purposes [like this](https://github.com/beacandler/EATEN).

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
python augment.py --config <config.json> --src_folder <input_folder> --epochs <num_epochs> --dest_folder 
<output_folder> --num_workers <num_workers>
```
e.g : python augment.py --config templates/sample_augmentation/config.json --src_folder output --epochs 10 --dest_folder output_augmented --num_workers 6

Check [`documentation/Augmentation`](documentation/Augmentation.md) for more details.

<hr/>

## Demo Web UI

Ensure you have installed StreamLit by `pip install streamlit`.

### Generator UI

UI to generate document using desired template by filling data manually (for demo purpose)

```
streamlit run generator_ui.py
```

ToDo: (Contributions welcome)

- Add augmentation support in UI
- Create another UI for creating templates.

<hr/>

## Footnotes

For any problems or queries, please report under the "Issues" tab.  
Feel free to contribute by sending a Pull Request.

### Other similar libraries

- [DocCreator](https://doc-creator.labri.fr/)
- [DocEmul](https://github.com/narVidhai/DocEmul)
