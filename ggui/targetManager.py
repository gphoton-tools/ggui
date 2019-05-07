from collections import OrderedDict

from PyQt5 import QtWidgets, QtGui
from glue.core.link_helpers import LinkSame
from glue.core.data_factories import load_data

from pkg_resources import resource_filename

class target_manager(QtWidgets.QToolBar):
    """
    Class that handles the loading of gPhoton data and management of multiple
    gGui targets
    """
        """Initializes gGui Target Manager
        If provided a dictionary of targets, in outlined gGui YAML structure, it will load those targets into the target manager

        :param GlueApplication: The Glue instance that instantiated this object. Target Manager cannot be run outside a Glue context
        :param target_change_callback: Callback function to notify upon primary target change
        """
        super().__init__()
        self._glue_parent = glue_parent
        self._target_catalog = OrderedDict()
        self._primary_name = ""
        self._primary_data = {}
        self._target_change_callbacks = []

        # Initialize GUI Elements
        self.addWidget(QtWidgets.QLabel("gGui Target Manager: "))
        # Add Back Button
        self.addAction(QtGui.QIcon(resource_filename('ggui.icons', 'ArrowBack_transparent.png')), "Previous Target", self.previous_target)
        # Add Combo Box
        self.QComboBox = QtWidgets.QComboBox(self)
        self.QComboBox.currentTextChanged.connect(self.setPrimaryTarget)
        self.addWidget(self.QComboBox)
        # Add Forward Button
        self.addAction(QtGui.QIcon(resource_filename('ggui.icons', 'ArrowForward_transparent.png')), "Next Target", self.next_target)

        # If the initializer wants to know about target changes, register its provided callback
        if target_change_callback:
            self.register_target_change_callback(target_change_callback)

    def register_target_change_callback(self, callback):
        """Registers a callback function to call when primary target changes

        :param callback: Callback function
        """
        self._target_change_callbacks.append(callback)
    
    def loadTargetDict(self, targDict: dict):
        """Loads a dictionary of targets and associated data product paths into internal cache

        :param targDict: gGui compliant dictionary of targets and paths to associated gPhoton data products
        """
        # Add incoming dictionary to internal cache
        self._target_catalog.update(targDict)
        # Add new items to GUI
        self.QComboBox.addItems(targDict.keys())

    def setPrimaryTarget(self, targName: str):
        """Changes primary target to target specified
        Unloads existing primary target's data (internal cache and parent Glue session), 
        loads the new primary target's data, links their corresponding attributes together,
        and notifies all stakeholders of the new changed primary target

        :param targName: Name of desired new primary target
        """
        # If requested target is not in current cache, throw exception
        if targName not in self._target_catalog.keys():
            raise KeyError("Target Manager does not recognize requested target: " + str(targName))
        # Don't bother doing anything if we're changing to the current target!
        if targName != self._primary_name:
            # If we have data loaded, remove it
            if self._primary_data: 
                def unload_primary_data():
                    for band_data_set in list(self._primary_data.values()):
                        for band_data in band_data_set.values():
                            self._glue_parent.data_collection.remove(band_data)                
                unload_primary_data()
            
            # Clear existing target cache
            self._primary_name = None
            self._primary_data.clear()
            
            target_files = self._target_catalog.get(targName)
            # For each gGui Data Type...
            for data_product_type in target_files:
                self._primary_data[data_product_type] = {}
                # Load every band's data
                for band, band_file in target_files[data_product_type].items():
                    if band_file:
                        self._primary_data[data_product_type][band] = load_data(band_file)
                        #confirm this is the same object as what was stored in the data collection:
                        self._glue_parent.data_collection.append(self._primary_data[data_product_type][band])
                # If we have multiple bands, glue them together
                #bands = self._primary_data[data_product_type].keys()
                if len(self._primary_data[data_product_type].keys()) > 1:
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

            # Now that all data has been processed properly, officially designate targName as new primary target
            self._primary_name = targName

            # Notify all stakeholders of target change
            for callback in self._target_change_callbacks:
                callback(self._primary_name)

    def getPrimaryData(self) -> dict:
        """Returns currently loaded primary target's data
        
        :returns: dictionary of the current primary target's data
        """
        return self._primary_data

    def getPrimaryName(self) -> dict:
        """Returns the current primary target's name

        :returns: current primary target's name as string
        """
        return self._primary_name

    def getTargetNames(self) -> list:
        """Returns a list of all cached targets' names
        
        :returns: list of all cached targets' names
        """
        return self._target_catalog.keys()

    def next_target(self):
        """Advances to next primary target"""
        # Determine the index we're switching to...
        current_target_index = list(self._target_catalog.keys()).index(self._primary_name)
        next_target_index = current_target_index + 1
        # And wrap around to the front if we're currently on the last target
        if next_target_index > int(len(self._target_catalog.keys())) - 1:
            next_target_index = 0
        # Command Target Manager to switch primary targets
        next_target_name = list(self._target_catalog.keys())[next_target_index]
        self.QComboBox.setCurrentText(next_target_name) # QComboBox signal will initiate primary target switching

    def previous_target(self):
        """Advances to previous primary target"""
        # Determine the index we're switching to...
        current_target_index = list(self._target_catalog.keys()).index(self._primary_name)
        next_target_index = current_target_index - 1
        # And wrap around to the back if we're currently on the first target
        if next_target_index < 0:
            next_target_index = int(len(self._target_catalog.keys())) - 1
        # Command Target Manager to switch primary targets
        next_target_name = list(self._target_catalog.keys())[next_target_index]
        self.QComboBox.setCurrentText(next_target_name) # QComboBox signal will initiate primary target switching