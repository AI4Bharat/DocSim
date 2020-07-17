# Installation

## Installing [`Raqm library`](https://github.com/HOST-Oman/libraqm) to use Complex fonts

### Linux

```sh
sudo apt install libfreetype6-dev libharfbuzz-dev libfribidi-dev gtk-doc-tools
sudo apt install libraqm-dev
```

### Windows

- Download `libraqm.dll` and `fribidi-0.dll` [from here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow).
- Place those 2 DLLs along with your installed `python.exe`. That's it.
- Or you can also put it in a folder of your choice and append that folder path to `PYTHONPATH` environment variable.
