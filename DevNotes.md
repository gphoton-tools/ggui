* DevNote 1: Python For Loop Scope
    Apparently variables defined within a for loop are still maintained after the loop exits. Ambiguous if this is a feature or bug. Not sure if utilizing this feature is "pythonic" but it appears this is a part of the language, so I'm going to use it...
    * https://stackoverflow.com/questions/3611760/scoping-in-python-for-loops
    * https://mail.python.org/pipermail/python-ideas/2008-October/002109.html

* DevNote2: Python Dict Order Preservation (PEP 468 )
    Starting Python 3.6, Python dictionaries automatically preserve order. Not sure what OrderedDicts are useful for now adays...
    * https://docs.python.org/3.6/whatsnew/3.6.html#new-dict-implementation