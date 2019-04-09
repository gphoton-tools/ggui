* DevNote 1: Python For Loop Scope
    Apparently variables defined within a for loop are still maintained after the loop exits. Ambiguous if this is a feature or bug. Not sure if utilizing this feature is "pythonic" but it appears this is a part of the language, so I'm going to use it...
    * https://stackoverflow.com/questions/3611760/scoping-in-python-for-loops
    * https://mail.python.org/pipermail/python-ideas/2008-October/002109.html

* DevNote 2: Python Dict Order Preservation (PEP 468 )
    Starting Python 3.6, Python dictionaries automatically preserve order. Not sure what OrderedDicts are useful for now adays...
    * https://docs.python.org/3.6/whatsnew/3.6.html#new-dict-implementation

* DevNote 3: How to run setup.py
    1. Create distribution: python setup.py sdist
    2. Extract sdist into test directory
    3. Create venv
    4. pip install bottleneck==1.2.1
    5. python setup.py install
    6. pip uninstall pyqt5
    7. pip install --upgrade pyqt5
    8. ggui
    NOTE: Had to change imports in copied source code to import ggui modules from ggui package (i.e. 'import qtTabLayouts' > 'from ggui import qtTabLayouts)