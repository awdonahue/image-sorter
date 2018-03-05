# Image Sorter

## Introduction
Python script that will sort images into dated folders based off the images metadata

**Requirements**:
- Python >= 3.6.3
- Required Packages:
  - exifread
- [See here](https://devdocs.io/python~3.6/library/imghdr#imghdr.what) for supported image types

## Setup
---
1. Install python3

2. Install python packages (from working directory)
```bash
pip3 install -r requirements.txt
```


## Usage
---

To run the script with default args, run:
```bash
python3 ImageSorter.py [path/to/images]
```

The following args can be passed to config the script:

| Arg                                  | Type       | Default Value       | Description |
| ------------------------------------ | ---------- | ------------------- | ----------- |
| `-h` or `--help`                     | optional   | N/A                 | A quick reference on how to use the script |
| `-o` or `--output`                   | optional   | `tmp/images-sorted` | Target designation of sorted images |
| `-d` or `--depth` `<year,month,day>` | optional   | `month`             | Folder depth on how to sort images |
| `-m` or `--move`                     | optional   | `False`             | Move the images instead of copying them |
| `-l` or `--log`                      | optional   | `False`             | Log the process in a report log file |
| `dir`                                | positional | N/A                 | Where the image files are stored |

Example usage to move images from dir `~/Pictures/MyPics` into year folders (ie. `2017/`, `2016/`):
```bash
~$ python ImageSorter.py -m -d year ~/Pictures/MyPics
```
