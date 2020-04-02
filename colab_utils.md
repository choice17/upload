# Colab utils

* Copy colab utils function

```
!pip install -U -q PyDrive
!git clone https://github.com/Joshua1989/python_scientific_computing.git
!git clone https://gist.github.com/dc7e60aa487430ea704a8cb3f2c5d6a6.git /tmp/colab_util_repo
!mv /tmp/colab_util_repo/colab_util.py colab_util.py 
!rm -r /tmp/colab_util_repo
```
* Specify colab tensorflow version

```
%tensorflow_version 1.x
```

* import google driver handler and drive

```
from colab_util import *
drive_handler = GoogleDriveHandler()
```

```
from google.colab import drive
drive.mount('/content/gdrive')
```

* Control file systems between colab and gdrive

```
!ls /content/gdrive/My\ Drive/colab/dataset/*
```
