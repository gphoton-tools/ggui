"""
.. module:: qtTabLayouts
    :synopsis: Defines the gGui Target Manager to manage multiple targets
.. moduleauthor:: Duy Nguyen <dnguyen@nrao.edu>
"""

from collections import OrderedDict
from configparser import ConfigParser
import itertools
from typing import Callable
from copy import copy
import yaml

from PyQt5 import QtWidgets, QtGui
from glue.app.qt.application import GlueApplication
from glue.core.link_helpers import LinkSame
from glue.core.data_factories import load_data

from pkg_resources import resource_filename


class target_manager(QtWidgets.QToolBar):
    """
    Class that handles the loading of gPhoton data and management of multiple
    gGui targets
    """
    def __init__(self, glue_parent: GlueApplication, target_change_callback: Callable[[str], None] = None):
        """Initializes gGui Target Manager
        If provided a dictionary of targets, in outlined gGui YAML structure, it will load those targets into the target manager

        :param glue_parent: The Glue instance that instantiated this object. Target Manager cannot be run outside a Glue context
        :param target_change_callback: Callback function to notify upon primary target change
        """
        super().__init__()
        self._glue_parent = glue_parent
        self._target_catalog = OrderedDict()
        self._primary_name = ""
        self._primary_data = {}
        self._target_change_callbacks = []
        self._target_notes = None
        self._note_display_widget = target_note_display(self)

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
        # Add Notes Button
        self.addAction(QtGui.QIcon(resource_filename('ggui.icons', 'Notepad.png')), "Target Notes", self._note_display_widget.show)

        # If the initializer wants to know about target changes, register its provided callback
        if target_change_callback:
            self.register_target_change_callback(target_change_callback)

    def close(self):
        """Handles graceful exit housekeeping"""

        # Close note display widget if open
        self._note_display_widget.close()

    def register_target_change_callback(self, callback):
        """Registers a callback function to call when primary target changes

        :param callback: Callback function
        """
        self._target_change_callbacks.append(callback)

    def loadTargetDict(self, target_files: dict, id_name: str = None):
        """Loads a single dictionary of targets and associated data product paths into internal cache

        :param id_name: Name/identifier of this dictionary of targets. Can be used to return data
        :param target_files: gGui compliant yaml dictionary of targets and paths to associated gPhoton data products
        """
        # Add targets to internal cache
        self._target_catalog[id_name] = OrderedDict(target_files)
        # Add new items to GUI
        self.QComboBox.addItems(target_files.keys())

    def setPrimaryTarget(self, targName: str):
        """Changes primary target to target specified
        Unloads existing primary target's data (internal cache and parent Glue session), 
        loads the new primary target's data, links their corresponding attributes together,
        and notifies all stakeholders of the new changed primary target

        :param targName: Name of desired new primary target
        """
        # If requested target is not in current cache, throw exception
        if targName not in self.getTargetNames():
            raise KeyError("Target Manager does not recognize requested target: " + str(targName))
        # Don't bother doing anything if we're changing to the current target!
        if targName != self._primary_name:
            # If we have data loaded, remove it from the Glue Data
            if self._primary_data:
                def unload_primary_data():
                    for band_data_set in list(self._primary_data.values()):
                        for band_data in band_data_set.values():
                            if isinstance(band_data, list):
                                for data in band_data:
                                    self._glue_parent.data_collection.remove(data)   
                            else:
                                self._glue_parent.data_collection.remove(band_data)                
                unload_primary_data()

            # Save target notes
            self._note_display_widget.save_notes()

            # Clear internal target cache
            self._primary_name = None
            self._primary_data.clear()
            self._target_notes = None

            target_files = copy(self.getTargetFiles(targName))
            self._target_notes = target_files.pop('_notes', None)

            # For each gGui Data Type...
            for data_product_type in target_files:
                # Initialize dictionary for this data product
                self._primary_data[data_product_type] = {}

                # Retrieve the x and y attributes for this data product from the conf file
                config = ConfigParser()
                config.read(resource_filename('ggui', 'ggui.conf'))                
                x_att = config.get('Mandatory Fields', data_product_type + "_x", fallback='')
                y_att = config.get('Mandatory Fields', data_product_type + "_y", fallback='')

                # Load every band's data into internal cache
                for band, band_file in target_files[data_product_type].items():
                    if band_file:
                        self._primary_data[data_product_type][band] = load_data(band_file)

                        # If x_att, y_att provided in conf, test they exist
                        try:
                            if x_att:
                                self._primary_data[data_product_type][band].id[x_att]
                            if y_att:
                                self._primary_data[data_product_type][band].id[y_att]
                        # KeyError means specified attribute doesn't exist in this data. Warn user, and unset attributes, but continue
                        except KeyError as e:
                            parsed_error = e.args[0].split(':')
                            if parsed_error[0]== 'ComponentID not found or not unique':
                                print("WARNING: '" + parsed_error[1].strip() + "' field specified in ggui.conf missing from " + targName + " " + data_product_type + " " + band + ": " + band_file)
                                x_att = ''
                                y_att = ''
                            else:
                                raise
                        # If AttributeError, check if "data" is actually a list of data (multiple data sets per file). Breaks 1-1 correspondence gGui assumes. Warn user plotting and gluing will fail. Skip this data, but import it regardless
                        except AttributeError:
                            if isinstance(self._primary_data[data_product_type][band], list):
                                print("WARNING: " + str(len(self._primary_data[data_product_type][band])) + " datasets imported from " + targName + " " + data_product_type + " band " + band + ". gGui shall import this data, but will be unable to perform automatic actions on it (i.e. gluing, displaying overview, etc.)")
                            else:
                                raise
                            
                        # Register this data product with Glue's Data Collection
                        self._glue_parent.data_collection.append(self._primary_data[data_product_type][band])
                # If we have multiple bands, glue them together
                try: 
                    if len(self._primary_data[data_product_type].keys()) > 1:
                        attributes_to_glue = {'lightcurve': ['t_mean', 'flux_bgsub'], 
                                            'coadd': ['Right Ascension', 'Declination'], 
                                            'cube': ['Right Ascension', 'Declination', 'World 0']}
                        #for glue_attribute in attributes_to_glue[data_product_type]:
                        for glue_attribute in list(filter(lambda x: x is not '', [x_att, y_att] + config.get('Additional Fields To Glue', data_product_type, fallback='').split(','))):
                            #Can only link two fields at a time. Need to go through all combinations
                            from itertools import permutations
                            for linking_pair in (set(frozenset(t) for t in permutations(self._primary_data[data_product_type].values(),2))):
                                accessor = tuple(linking_pair)
                                self._glue_parent.data_collection.add_link(LinkSame(accessor[0].id[glue_attribute],accessor[1].id[glue_attribute]))
                except TypeError as e:
                    print("Unable to glue " + str(targName) + " " + str(data_product_type) + ": " + str(e))
            
            # Now that all data has been processed properly, officially designate targName as new primary target
            self._primary_name = targName

            # Notify all stakeholders of target change
            for callback in self._target_change_callbacks:
                callback(self._primary_name)

    def setPrimaryNotes(self, new_notes: str):
        """"
        Updates internal cache of target's notes to given string

        :param new_notes: New notes for the primary target
        """
        self._target_notes = new_notes
        self.getTargetFiles(self._primary_name)['_notes'] = new_notes

    def getTargetNames(self) -> list:
        """Returns the names of all registered targets, in their registered order

        :returns: list of all cached targets' names
        """
        # Devnote 8: List Comprehension Alternative
        return list(itertools.chain.from_iterable(self._target_catalog.values()))

    def getTargetFiles(self, target_name: str) -> dict:
        """Returns the files and metadata of a specified target (Unloaded data, as per lazy evaluation principle)
        
        :param target_name: Name of the target whose files to lookup
        :returns: Unloaded metadata and filepaths of the corresponding target's data
        """
        for target_data_catalog in self._target_catalog.values():
            try:
                return target_data_catalog[target_name]
            except KeyError:
                pass
        raise KeyError("'" + str(target_name) + "' not found in cache")

    def getTargetNotes(self, target_name: str) -> str:
        """Returns the notes specified target, or blank string if no notes registered
        
        :param target_name: Name of the target whose notes to lookup
        :returns: Notes of the specified target, or blank string if no notes
        """
        targ_data = self.getTargetFiles(target_name)
        try:
            return targ_data['_notes']
        except KeyError:
            return ""
    
    def getTargetSourceFile(self, target_name: str) -> str:
        """Returns the source yaml file the given target originated from
        
        :param target_name: Name of the target whose source yaml file to lookup
        :returns: Absoute filepath of the specified target's source file.
        """
        for source_filename, target_data_catalog in self._target_catalog.items():
            if target_name in target_data_catalog:
                return source_filename
        raise KeyError("Source file for target '" + str(target_name) + "' could not be found")

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

    def getPrimaryNotes(self) -> str:
        """Returns any notes associated with the current target. Returns empty string if no notes found.

        :returns: notes registered with the current target
        """
        return self._target_notes

    def next_target(self):
        """Advances to next primary target"""
        # Determine the index we're switching to...
        current_target_index = list(self.getTargetNames()).index(self._primary_name)
        next_target_index = current_target_index + 1
        # And wrap around to the front if we're currently on the last target
        if next_target_index > int(len(self.getTargetNames())) - 1:
            next_target_index = 0
        # Command Target Manager to switch primary targets
        next_target_name = list(self.getTargetNames())[next_target_index]
        self.QComboBox.setCurrentText(next_target_name) # QComboBox signal will initiate primary target switching

    def previous_target(self):
        """Advances to previous primary target"""
        # Determine the index we're switching to...
        current_target_index = list(self.getTargetNames()).index(self._primary_name)
        next_target_index = current_target_index - 1
        # And wrap around to the back if we're currently on the first target
        if next_target_index < 0:
            next_target_index = int(len(self.getTargetNames())) - 1
        # Command Target Manager to switch primary targets
        next_target_name = list(self.getTargetNames())[next_target_index]
        self.QComboBox.setCurrentText(next_target_name) # QComboBox signal will initiate primary target switching

    def flushSourceFile(self, source_filename: str):
        """Force saves (flushes) the given source file
        Intended to be used for saving notes

        :param source_filename: Filename of source file to be flushed
        """
        with open(source_filename, "w") as source_file:
            source_file.write(yaml.dump(dict(self._target_catalog[source_filename])))

class target_note_display(QtWidgets.QGroupBox):
    """Subwidget to display notes of current target"""

    def __init__(self, parent):
        """
        Initializes note display widget

        :param parent: The parent that spawned this note widget (usually the target manager)
        """
        super().__init__()
        self._target_manager = parent
        self._target_manager.register_target_change_callback(self.primary_target_changed)
        # Initialize Widgets
        # Main Text Field
        self._text_field = QtWidgets.QTextEdit()
        self._text_field.document().modificationChanged.connect(self.modificationChanged)
        # Save Notes Button
        self._save_button = QtWidgets.QPushButton("Save Notes")
        self.setTitle("Notes: Unmodified")
        self._save_button.setEnabled(False)
        self._save_button.clicked.connect(lambda: self.save_notes(True))
        # Discard Changes Button
        self._discard_button = QtWidgets.QPushButton("Discard Changes")
        self._discard_button.clicked.connect(self.discard_note_changes)
        self._discard_button.setEnabled(False)
        # Declare Layout
        self._layout = QtWidgets.QGridLayout()
        self.setLayout(self._layout)
        # Organize Widgets in Layout
        self._layout.addWidget(self._text_field, 0, 0, 1, 2)
        self._layout.addWidget(self._save_button, 1, 0)
        self._layout.addWidget(self._discard_button, 1, 1)

    def closeEvent(self, _):
        """When close is detected, prompts user to save notes if text has been modified"""
        self.save_notes()

    def primary_target_changed(self, new_target: str):
        """
        When primary target has changed, retrieves notes for the new target

        :param new_target: Name of the new primary target
        """
        # Get the new notes and update our text field
        self._text_field.setText(self._target_manager.getPrimaryNotes())
        # Set text field to unmodified to recalibrate autosave detection
        self._text_field.document().setModified(False)

    def save_notes(self, force_save: bool = False):
        """
        Checks if notes need to be saved. If so, saves the notes and flushes to disk

        :param force_save: If True, skips text modification checks and forces a save to disk
        """
        # Check for abort-save conditions
        if not force_save:
            # Check if text has been modified
            unsaved_text = self._text_field.document().isModified()
            # If text has been modified, ask user if they want to save. Otherwise, fallthrough to save
            if unsaved_text:
                if QtWidgets.QMessageBox.Cancel == QtWidgets.QMessageBox.question(self, "Close Confirmation", "Do you want to save changes to your notes?", QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel):
                    return
            # If text hasn't been modified, exit
            else:
                return
        # If no abort-save conditions caught, save to disk
        self._target_manager.setPrimaryNotes(self._text_field.toPlainText())
        try:
            self._target_manager.flushSourceFile(self._target_manager.getTargetSourceFile(self._target_manager.getPrimaryName()))
            # Set text field to unmodified to recalibrate autosave detection
            self._text_field.document().setModified(False)
        except IOError:
            print("Error saving notes! Your notes have NOT been saved!")

    def discard_note_changes(self):
        """Discards any changes to notes and reverts to last saved notes"""

        # Safety Prompt
        if QtWidgets.QMessageBox.Cancel == QtWidgets.QMessageBox.question(self, "Discard Confirmation", "Are you sure you want to permanently discard changes to your notes?", QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel):
            return
        # Revert Notes
        self._text_field.setText(self._target_manager.getPrimaryNotes())
        # Set text field to unmodified to recalibrate autosave detection
        self._text_field.document().setModified(False)
        self.setTitle("Notes: Changes Discard")
        self.setStyleSheet('QGroupBox:title {color: rgb(0, 0, 175);}')

    def modificationChanged(self, changed: bool):
        self._save_button.setEnabled(changed)
        self._discard_button.setEnabled(changed)
        if changed:
            self.setTitle("Notes: Modified")
            self.setStyleSheet('QGroupBox:title {color: rgb(255, 0, 0);}')
        else:
            self.setTitle("Notes: Saved")
            self.setStyleSheet('QGroupBox:title {color: rgb(0, 150, 0);}')
