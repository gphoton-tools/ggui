# gGui: gPhoton glue user interface.
gGui is a data-interpretation interface intended to interpet data from the GALEX Space Telescope data reduction pipeline, [gPhoton](https://archive.stsci.edu/prepds/gphoton/). 

GALEX was an ultraviolet space telescope commissioned by NASA and managed by the Jet Propulsion Laboratory (JPL) at the California Institute of Technology (CalTech). The data currently resides at the [Space Telescope Science Institute's](http://www.stsci.edu/) (STScI) [Mikulski Archive for Space Telescopes](http://archive.stsci.edu/index.html) (MAST).

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
