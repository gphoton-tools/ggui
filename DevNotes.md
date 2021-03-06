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

* Devnote 4: Documenting callback function argument
    PEP-0484, the PEP that introduced function annotations, has a section on this: https://www.python.org/dev/peps/pep-0484/#callable
    * Found via: https://stackoverflow.com/questions/33399232/is-there-a-standard-way-to-specify-the-type-of-a-callback-function-in-a-docstrin

* Devnote 5: If git reset --hard, ALWAYS STASH FIRST

* Devnote 6: Glue Data object is iterable, but usually not in the ways you think. Most operations with list comprehension will fail

* Devnote 7: Sphinx version 2.0 changed default master_doc from index.rst/html to contents.rst/html

* Devnote 8: Could also be replaced with list comprehension, but this itertools seems to be more human readable (at least to me) and according to the stackoverflow I found it on, it is also faster:
  * https://stackoverflow.com/questions/14807689/python-list-comprehension-to-join-list-of-lists
  * return [item for sublist in [x.keys() for x in self._target_catalog.values()] for item in sublist]