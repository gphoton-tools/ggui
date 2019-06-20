# gGui: gPhoton glue user interface.
gGui is a data-analysis software written to visualize astronomical data, specifically time-tagged lightcurves, coadds, and cubes. gGui serves as the primary data visualization tool for [gPhoton](https://archive.stsci.edu/prepds/gphoton/), the data reduction pipeline for GALEX. 

Please see our full documentation at: https://ggui.readthedocs.io/

gGui is written atop the [Glue Python Library for Dataset Visualization](https://github.com/glue-viz/glue). 

## Installation Instructions:
* Install via pip
```console
pip install ggui
```

## Sample Usage
* If you know where your yaml file lives, you can specify it as a line argument:
```console
ggui --target_list /path/to/ggui.yml
```
* If you'd like to graphically search for your yaml, ggui can create a file selector dialog for you:
```console
ggui --yaml_select
```

## Revision History
2019-06-11: Uploaded first test of b0.3.5 to PyPI
2017-06-26: v0.3.0 Tag Created
