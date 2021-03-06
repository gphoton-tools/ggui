# gGui: gPhoton glue user interface.
gGui is a data-analysis software written to visualize astronomical data, specifically time-tagged lightcurves, coadds, and cubes. gGui serves as the primary data visualization tool for [gPhoton](https://archive.stsci.edu/prepds/gphoton/), the data reduction pipeline for GALEX. 

Please see our full documentation at: https://ggui.readthedocs.io/

gGui is written atop the [Glue Python Library for Dataset Visualization](https://github.com/glue-viz/glue). 

## Installation Instructions:
* Install Python 3.6+
* Upgrade pip
```console
python -m pip install --upgrade pip
```
* Install gGui via pip
```console
pip install ggui
```

## Sample Usage
```console
ggui --target_list /path/to/ggui.yml
```
will automatically load a specific target list into a new gGui session.
```console
ggui --yaml_select
```
will open a file-select dialog to select your target list(s). After which, gGui will load these targets.

## Major Revision History
* 2019-12-22: Version 1.2 posted to GitHub/PyPI
* 2019-11-02: Version 1.1 posted to GitHub/PyPI
* 2019-06-20: Version 1.0 posted to GitHub/PyPI
* 2019-06-11: Uploaded first test of b0.3.5 to PyPI
* 2017-06-26: v0.3.0 Tag Created
