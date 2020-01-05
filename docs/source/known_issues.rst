Known Issues with gGui
######################
If you run into any issues with gGui, please let us know by creating a GitHub issue! We'd rather an issue get reported multiple times than it not be reported at all! Listed below are known issues with gGui. Please reference this page if you are getting stuck.

* gGui abruptly crashes upon unrecognized field in [Additional Fields to Glue] heading in ggui.conf
* We are aware of installation issues for users who wish not to use pip and instead invoke our setup.py directly. To install ggui from source without using pip, please note a workaround we have found to be successful:

    1. Clone source from GitHub into an empty directory: ``git clone https://github.com/gphoton-tools/ggui.git .``
    2. ``python ./setup.py install`` from local git root
    3. Modify qtpy to use PyQt5 instead of PySide

        a. Determine qtpy initialization file from python interpreter: ``import qtpy; qtpy.__file__``
        b. Open this file and determine where the PYSIDE_API detection occurs (As of QtPy version 1.9.0, this occurs around line 202)
        c. Modify the qtpy initialization file by adding ``API = 'pyqt5'`` to PySide detection. The file should read:
            
            ::

                ...
                API = 'pyqt5' #Add this line
                if API in PYSIDE_API:
                    try:
                        from PySide import __version__ as PYSIDE_VERSION  # analysis:ignore
                ...
    4. Uninstall PyQt5 and PyQt5-sip:

        a. ``pip uninstall PyQt5``
        b. ``pip uninstall PyQt5-sip``
    5. Reinstall PyQt5, which will automatically install PyQt5 as dependency: ``pip install PyQt5``
    6. You should now be able to start ggui normally
