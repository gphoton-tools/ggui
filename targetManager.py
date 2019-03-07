from collections import OrderedDict

from PyQt5 import QtWidgets, QtCore, QtGui
from glue.core.link_helpers import LinkSame
from glue.core.data_factories import load_data

import pathlib

class target_manager(QtWidgets.QToolBar):
    """
    Class that handles the loading of gPhoton data and management of multiple
    gGui targets
    """
    def __init__(self, glue_parent):
        super().__init__()
        self._glue_parent = glue_parent
        self._target_catalog = OrderedDict()
        self._primary_name = ""
        self._primary_data = {}

        # Initialize GUI Elements
        self.addWidget(QtWidgets.QLabel("gGui Target Manager: "))
        # Add Back Button
        self.addAction(QtGui.QIcon(str(pathlib.Path.cwd() / 'icons' / 'ArrowBack.png')), "Backward", self.previous_target)
        # Add Combo Box
        self.QComboBox = QtWidgets.QComboBox(self)
        self.QComboBox.currentTextChanged.connect(self.targClick)
        self.addWidget(self.QComboBox)
        # Add Forward Button
        self.addAction(QtGui.QIcon(str(pathlib.Path.cwd() / 'icons' / 'ArrowForward.png')), "Forward", self.next_target)

    def targClick(self, target_name):
        if target_name is not self._primary_name:
            self.setPrimaryTarget(target_name)
            self._glue_parent.overview_tab.load_data(self._glue_parent.session,
                                                     self.getPrimaryName(),
                                                     self.getPrimaryData())
    
    def loadTargetDict(self, targDict: dict):
        # Add incoming dictionary to internal cache
        self._target_catalog.update(targDict)
        # Add new items to GUI
        self.QComboBox.addItems(targDict.keys())

    def setPrimaryTarget(self, targName: str):
        # Don't bother doing anything if we're changing to the current target!
        if targName is not self._primary_name:
            # If we have data loaded, remove it
            if self._primary_data: 
                def unload_primary_data():
                    for band_data_set in list(self._primary_data.values()):
                        for band_data in band_data_set.values():
                            self._glue_parent.data_collection.remove(band_data)                
                unload_primary_data()
            
            # Set GUI's primary target to specified
            self.QComboBox.setCurrentText(targName)
            
            # Clear existing target cache
            self._primary_name = targName
            self._primary_data.clear()
            
            target_files = self._target_catalog.get(self._primary_name)
            # For each gGui Data Type...
            for data_product_type in target_files:
                self._primary_data[data_product_type] = {}
                # Load every band's data
                for band, band_file in target_files[data_product_type].items():
                    self._primary_data[data_product_type][band] = load_data(band_file)
                # If we have multiple bands, glue them together
                bands = self._primary_data[data_product_type].keys()
                if len(bands) > 1:
                    attributes_to_glue = {'lightcurve': ['t_mean', 'flux_bgsub'], 
                                        'coadd': ['Right Ascension', 'Declination'], 
                                        'cube': ['Right Ascension', 'Declination', 'World 0']}
                    for glue_attribute in attributes_to_glue[data_product_type]:
                        #dataCollection.add_link(LinkSame(somehow add all bands here stored in the bands key above))
                        #Can only link two fields at a time. Need to go through all combinations
                        import itertools
                        for linking_pair in (set(frozenset(t) for t in itertools.permutations(self._primary_data[data_product_type].values(),2))):
                        #for linking_pair in (set(tuple(sorted(t)) for t in itertools.permutations(self._primary_data['lightcurve'].values(),2))):
                            accessor = tuple(linking_pair)
                            self._glue_parent.data_collection.add_link(LinkSame(accessor[0].id[glue_attribute],accessor[1].id[glue_attribute]))
                            #self._glue_parent.data_collection.add_link(LinkSame(linking_pair[0].id[glue_attribute]))

    def getPrimaryData(self):
        return self._primary_data

    def getPrimaryName(self):
        return self._primary_name

    def getTargetNames(self):
        return self._target_catalog.keys()

    def next_target(self):
        # Determine the index we're switching to...
        current_target_index = list(self._target_catalog.keys()).index(self._primary_name)
        next_target_index = current_target_index + 1
        # And wrap around to the front if we're currently on the last target
        if next_target_index > int(len(self._target_catalog.keys())) - 1:
            next_target_index = 0
        # Command Target Manager to switch primary targets
        next_target_name = list(self._target_catalog.keys())[next_target_index]
        self.setPrimaryTarget(next_target_name)

    def previous_target(self):
        # Determine the index we're switching to...
        current_target_index = list(self._target_catalog.keys()).index(self._primary_name)
        next_target_index = current_target_index - 1
        # And wrap around to the back if we're currently on the first target
        if next_target_index > 0:
            next_target_index = int(len(self._target_catalog.keys())) - 1
        # Command Target Manager to switch primary targets
        next_target_name = list(self._target_catalog.keys())[next_target_index]
        self.setPrimaryTarget(next_target_name)

    