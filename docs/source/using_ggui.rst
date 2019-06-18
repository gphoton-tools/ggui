Using gGui
##########

Installing gGui
===============
gGui is hosted on `PyPI <https://pypi.org/project/ggui/>`_. To install, simply use pip:
::

    pip install ggui

Alternatively you may download and install directly from our GitHub repository, again using pip:
::

    git clone https://github.com/gphoton-tools/ggui.git
    pip install ./ggui

gGui Target List
================
gGui ingests a list of targets and associated paths to data products. To create this file, you can use our ``make_param`` utility.

Alternatively, you can write this file yourself. This file is written in the YAML standard and expects the following format:
::

    <Target Name>
        <Data Product Type>
            <Band>: <Absolute path to file>

for example:
::

    Andromeda Galaxy
        lightcurve
            NUV: /home/ggui_data/andromeda_nuv_lightcurve.csv
            FUV: /home/ggui_data/andromeda_fuv_lightcurve.csv
        coadd
            NUV: /home/ggui_data/andromeda_nuv_coadd.fits
        cube
            NUV: /home/ggui_data/andromeda_nuv_cube.fits
            FUV: /home/ggui_data/andromeda_fuv_cube.fits

gGui Configuration File
=======================
gGui configures itself, and its environment, using a python configuration file: ``ggui.conf``. This file is located with the source code (the result of ``import ggui; import os; os.path.dirname(ggui.__file__)``) and should be modified to fit your needs. The configuration file contains two fields. 

``[Mandatory Fields]`` defines which fields will be assigned to which axes. gGui comes out-of-the-box configured for gPhoton lightcurves, coadds, and cubes:
::

    [Mandatory Fields]
    lightcurve_x = t_mean
    lightcurve_y = flux_bgsub

    coadd_x = Right Ascension
    coadd_y = Declination

    cube_x = Right Ascension
    cube_y = Declination

If multiple bands are provided for each data product type (i.e. lightcurves, coadds, cubes), gGui will automatically attempt to `glue <http://docs.glueviz.org/en/stable/getting_started/index.html#linking-data>`_ these fields together.

``[Additional Fields to Glue]`` defines additional fields gGui should associate, and therefore glue together. Multiple fields can be specified, comma delimited. Once again, gGui is configured by default for gPhoton data products:
::

    [Additional Fields To Glue]
    cube = World 0
    lightcurve = t0,t1

Running gGui
============
Assuming you have a properly formatted target list, and have configured the gGui fields of your data, gGui can be started with two independent flags:

``ggui --target_list <path to gGui Target List>`` will automatically load a specific target list into a gGui session.

``ggui --yaml_select`` will open a file select dialog to select your target list(s). After which, gGui will load these targets.

If you are in an IPython environment, you can invoke gGui's main() function to use these flags as well: ``from ggui import ggui; ggui.main(['--target_list', '<path to gGui Target List'])``