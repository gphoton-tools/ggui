from collections import OrderedDict

from PyQt5 import QtWidgets, QtCore
from glue.config import menubar_plugin
from glue.core.link_helpers import LinkSame
from glue.core.data_factories import load_data

class target_manager(QtWidgets.QWidget):
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
        self.setWindowTitle("gGui Target Manager")
        self.setGeometry(100,100,200,50)
        self.QListWidget = QtWidgets.QListWidget(self)
        self.QListWidget.itemClicked.connect(self.targClick)

    def targClick(self, item):
        if item.text() is not self._primary_name:
            self.setPrimaryTarget(item.text())
            self._glue_parent.overview_tab.load_data(self._glue_parent.session,
                                                     self.getPrimaryName(),
                                                     self.getPrimaryData())
    
    def loadTargetDict(self, targDict):
        # Add incoming dictionary to internal cache
        self._target_catalog.update(targDict)
        # Add new items to GUI
        self.QListWidget.addItems(targDict.keys())

    def setPrimaryTarget(self, targName):
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
            self.QListWidget.setCurrentItem(self.QListWidget.findItems(targName, QtCore.Qt.MatchExactly)[0])
            
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
        current_target_index = list(self._target_catalog.keys()).index(self._primary_name)
        next_target_index = current_target_index + 1
        if next_target_index > int(len(self._target_catalog.keys())) - 1:
            next_target_index = 0
        next_target_name = list(self._target_catalog.keys())[next_target_index]
        self.setPrimaryTarget(next_target_name)

    
@menubar_plugin("Next Target")
def next_target_plugin(session, _):
    # Command gGui to advance targets
    session.application.next_target()

