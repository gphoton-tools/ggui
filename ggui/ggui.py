"""
.. module:: gguicli_startup
    :synopsis: Startup script to import gPhoton data products into Glue Data Visualizer
.. moduleauthor:: Duy Nguyen <dtn5ah@virginia.edu>
"""

import argparse
import pathlib
import yaml

from glue.core import DataCollection
from glue.app.qt.application import GlueApplication
from glue.config import menubar_plugin
from PyQt5 import QtWidgets

from ggui import qtTabLayouts
from ggui.targetManager import target_manager

class ggui_glue_application(GlueApplication):
    """
    Primary gGui Application Class. Integrates gGui framework into Glue 
    (target manager, custom tab generation, etc.)
    """
    
    def __init__(self, data_collection=DataCollection(), target_dict={}):
        super().__init__(data_collection)
        # Save a reference to the default tab. We won't need this, but can't delete it until we have multiple tabs
        default_tab = self.current_tab
        
        # Initialize blank overview tab
        def init_overview_tab(self):
            # Initialize blank overview_widget
            self.overview_widget = qtTabLayouts.overviewTabLayout(session=self.session)
            self.tab_widget.addTab(self.overview_widget, "gGui Overview Tab: No Data Loaded")
            # Set Overview Tab to focus
            self.tab_widget.setCurrentWidget(self.overview_widget)
        init_overview_tab(self)

        # Initialize empty Target Manager
        self.target_manager = target_manager(self, self.primary_target_changed)
        self.addToolBar(self.target_manager)

        if target_dict:
            # Because we don't have a Multi-Target Manager yet, just choose the first one and load that one into gGui
            targ_names = list(self.target_manager.getTargetNames())
            print(str(len(target_dict.keys())) + " targets received. Loading " + str(list(target_dict.keys())[0]) + " as default.")

            # NOTE: Upon first load, Target Manager will automatically update target manager's primary target with the first entry in this dict.
            self.load_targets(target_dict)

        # Delete first default tab
        self.close_tab(self.get_tab_index(default_tab), False)

    def primary_target_changed(self, _):
        # Update all tabs with new target info
        self.overview_widget.load_data(self.session,
                                    self.target_manager.getPrimaryName(),
                                    self.target_manager.getPrimaryData())
        self.tab_widget.setTabText(self.get_tab_index(self.overview_widget), "Overview of " + str(self.target_manager.getPrimaryName()))

    def load_targets(self, target_dict: dict):
        """
        Imports gGui-compliant data (see yaml standard) into
        target manager

        :param target_dict: Dictionary of gPhoton data files with target name and corresponding band
        """
        self.target_manager.loadTargetDict(target_dict)

    def create_overview_widget(self, target_name: str, target_data: dict):
        """
        Creates an overview tab of gPhoton lightcurve, coadd, and cube data.
        Automatically constructs the tab, adds it to gGui and sets focus to it.

        :param target_name: The name of the target
        :param target_data: The corresponding gPhoton data of the target
        """
        self.overview_widget = qtTabLayouts.overviewTabLayout(session=self.session, targName=target_name, targData=target_data)
        #overview_widget.subWindowActivated.connect(self._update_viewer_in_focus)

        self.tab_widget.addTab(self.overview_widget, "Overview of " + str(target_name))
        # Set Overview Tab to focus
        self.tab_widget.setCurrentWidget(self.overview_widget)

def main(user_arguments: list = None):
    """Entry point/helper function to start ggui

    :param user_arguments: list of arguments, should simulate command line args. Use ['-h'] or ['--help'] for help documentation
    """
    # Initialize argument parser with arguments
    parser = argparse.ArgumentParser(description='gPhoton Graphical User Interface. An analysis package for GALEX gPhoton data products')
    parser.add_argument('--target_list', help='Specify a path to a YAML style list of astronomical targets and associated gPhoton data products')
    parser.add_argument('--yaml_select', action="store_true", help='Spawns a file select dialog to choose a YAML style list of astronomical targets and associated gPhoton data products')
    if user_arguments: 
        args = parser.parse_args(user_arguments)
    else: 
    args = parser.parse_args()
    
    target_data_products = {}
    # If the user specified a gGui YAML file, load its targets
    if args.target_list:
        print("File received: " + str(args.target_list))
        target_list_path = pathlib.Path(args.target_list)
        target_data_products.update(yaml.load(open(str(target_list_path), 'r')))
    # If the user requested a file-selector dialog to select a gGui YAML file, display it and load its contents
    if args.yaml_select:
        def prompt_user_for_file(dialogCaption: str, dialogNameFilter: str) -> list:
            """
            Modular QtWidget File-Selection Dialog to prompt user for file import.
            Returns array of filenames selected

            :param dialogCaption: Caption to display along top of file dialog window
            :param dialogNameFilter: Filters file dialog to certain extension
            """
            x = QtWidgets.QApplication([])
            # Set File Dialog Options
            dialog = QtWidgets.QFileDialog(caption=dialogCaption)
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
            dialog.setNameFilter(dialogNameFilter)
            # Prompt User for file to import
            dialog.exec_()
            # Get array of File Names
            filenames = dialog.selectedFiles()
            return filenames
        for ggui_yaml_file in prompt_user_for_file("Select GGUI YAML Target List", "gGUI YAML (*.yaml; *.yml)"):
            target_data_products.update(yaml.load(open(ggui_yaml_file, 'r')))
    # If no targets were recognized, notify the user
    if not target_data_products:
        print("No yaml received. Starting empty gGui session...")
    # Initialize gGui with user-supplied targets, if any
    ggui_app = ggui_glue_application(target_dict=target_data_products)
    # Start gGui
    ggui_app.start()
    
if __name__ == '__main__':
    main()
