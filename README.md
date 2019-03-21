# gGui: gPhoton glue user interface.
gGui is a data-interpretation interface intended to interpet data from the GALEX Space Telescope data reduction pipeline, [gPhoton](https://archive.stsci.edu/prepds/gphoton/). 

GALEX was an ultraviolet space telescope commissioned by NASA and managed by the Jet Propulsion Laboratory (JPL) at the California Institute of Technology (CalTech). The data currently resides at the [Space Telescope Science Institute's](http://www.stsci.edu/) (STScI) [Mikulski Archive for Space Telescopes](http://archive.stsci.edu/index.html) (MAST).

gGui is written atop the [Glue Python Library for Dataset Visualization](https://github.com/glue-viz/glue). 

## Prerequisits: 
* pipenv
* Python 3.7.1 64-bit

## Installation Instructions:
Inside the cloned directory:
```console
pipenv install
```
## Sample Usage
1. Activate your gGui pipenv environment:
```console
pipenv shell
```
2. Use the included CLI startup script:
```console
python .\ggui.py
```

## Revision History
2017-06-26: v0.3.0 Tag Created
