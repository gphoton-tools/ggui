"""
.. module:: ggui
    :synopsis: Defines the gGui class and startup behavior
.. moduleauthor:: Duy Nguyen <dnguyen@nrao.edu>
"""

import argparse
import pathlib
import yaml

from glue.core import DataCollection
from glue.app.qt.application import GlueApplication
from glue.config import menubar_plugin
import webbrowser
from glue.utils import nonpartial
from PyQt5 import QtWidgets

from ggui import qtTabLayouts
from ggui.targetManager import target_manager

from make_param import validate_targlist_format


class ggui_glue_application(GlueApplication):
    """Primary gGui Application Class
    Integrates gGui framework (target manager, custom tab generation, etc.) into Glue
    """

    def __init__(self, data_collection: DataCollection = DataCollection(), imported_target_catalogs: dict = None):
        """Initializes gGui
        If provided a dictionary of targets, in outlined gGui YAML structure, it will load those targets into the target manager

        :param data_collection: Glue data collection containing Glue data to plot
        :param imported_target_catalogs: Dict of targets and paths to associated gPhoton data products to load initially
        """
        super().__init__(data_collection)
        # Modify window title to specify gGui modified Glue environment
        self.setWindowTitle("gGui: gPhoton Graphical User Interface")
        # Add gGui YAML loader to "File" Menu
        self.menuBar().actions()[0].menu().addSeparator()
        self.menuBar().actions()[0].menu().addAction("Load gGui Target File", self.load_ggui_yaml)

        # Rename Glue "Help" to "About Glue"
        self.menuBar().actions()[6].setText("&About Glue")
        
        # Add "About gGui" Menu
        menu_about_ggui = self.menuBar().addMenu("About &gGui")
        # Add link to gGui ReadTheDocs
        ggui_rtd = QtWidgets.QAction("gGui &Online Documentation", menu_about_ggui)
        ggui_rtd.triggered.connect(nonpartial(webbrowser.open, 'https://ggui.readthedocs.io/'))
        menu_about_ggui.addAction(ggui_rtd)

        # Save a reference to the default tab. We won't need this, but can't delete it until we have multiple tabs
        default_tab = self.current_tab

        # Initialize blank overview tab
        def init_overview_tab(self):
            # Initialize blank overview_widget
            self.overview_widget = qtTabLayouts.ggui_overview_tab(session=self.session)
            self.tab_widget.addTab(self.overview_widget, "gGui Overview Tab: No Data Loaded")
            # Set Overview Tab to focus
            self.tab_widget.setCurrentWidget(self.overview_widget)
        init_overview_tab(self)

        # Initialize empty Target Manager
        self.target_manager = target_manager(self, self.primary_target_changed)
        self.addToolBarBreak()
        self.addToolBar(self.target_manager)

        if imported_target_catalogs:
            # Notify user of successful target catalog detection
            #print(str(len(imported_target_catalogs.keys())) + " targets received. Loading " + str(list(imported_target_catalogs.keys())[0]) + " as default.")

            # Load supplied target catalog into target manager
            # NOTE: Upon first load, Target Manager will automatically update target manager's primary target with the first entry in this dict.
            self.load_targets(imported_target_catalogs)

        # Delete first default tab
        self.close_tab(self.get_tab_index(default_tab), False)

    def closeEvent(self, event):
        """Handles subwindows when gGui is closed"""

        # Notify Target Manager of closing
        self.target_manager.close()

    def primary_target_changed(self, _):
        """Updates tab data of new primary target
        Indended as signal callback for the target manager to notify gGui of primary target changes
        """
        # Update overview tab with new target's data
        self.overview_widget.load_data(self.session,
                                       self.target_manager.getPrimaryName(),
                                       self.target_manager.getPrimaryData())
        self.tab_widget.setTabText(self.get_tab_index(self.overview_widget), "Overview of " + str(self.target_manager.getPrimaryName()))

    def load_targets(self, imported_target_catalogs: dict):
        """
        Imports gGui-compliant data (see yaml standard) into target manager

        :param imported_target_catalogs: Dict of gGui yamls and filenames imported from main
        """
        for filename in imported_target_catalogs:
            self.target_manager.loadTargetDict(imported_target_catalogs[filename], filename)

    def create_overview_widget(self, target_name: str, target_data: dict):
        """
        Creates an overview tab of gPhoton lightcurve, coadd, and cube data.
        Automatically constructs the tab, adds it to gGui and sets focus to it.

        :param target_name: The name of the target
        :param target_data: The corresponding gPhoton data of the target
        """
        self.overview_widget = qtTabLayouts.ggui_overview_tab(session=self.session, target_name=target_name, target_data=target_data)

        self.tab_widget.addTab(self.overview_widget, "Overview of " + str(target_name))
        # Set Overview Tab to focus
        self.tab_widget.setCurrentWidget(self.overview_widget)

    def load_ggui_yaml(self):
        """Prompts user with File Dialog for gGui YAML Target List
        Validates the YAML file and loads it into the Target Manager
        """
        for ggui_yaml_file in ggui_glue_application.prompt_user_for_file("Select GGUI YAML Target List", "gGUI YAML (*.yaml; *.yml)"):
            self.target_manager.loadTargetDict(validate_targlist_format(yaml.load(open(ggui_yaml_file, 'r'), Loader=yaml.BaseLoader), ggui_yaml_file), ggui_yaml_file)
    
    @staticmethod
    def prompt_user_for_file(dialogCaption: str, dialogNameFilter: str) -> list:
        """
        Modular QtWidget File-Selection Dialog to prompt user for file import.
        Returns array of filenames selected

        :param dialogCaption: Caption to display along top of file dialog window
        :param dialogNameFilter: Filters file dialog to certain extension
        """
        # Set File Dialog Options
        dialog = QtWidgets.QFileDialog(caption=dialogCaption)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        dialog.setNameFilter(dialogNameFilter)
        # Prompt User for file to import
        dialog.exec_()
        # Get array of File Names
        filenames = dialog.selectedFiles()
        return filenames


def main(user_arguments: list = None):
    """Entry point/helper function to start ggui

    :param user_arguments: list of arguments, should simulate command line args. Use ['-h'] or ['--help'] for help documentation
    """
    # Initialize argument parser with arguments
    parser = argparse.ArgumentParser(description='gPhoton Graphical User Interface. An analysis package for GALEX gPhoton data products')
    parser.add_argument('--target_list', nargs='+', help='Specify a path to a YAML style list of astronomical targets and associated gPhoton data products')
    parser.add_argument('--yaml_select', action="store_true", help='Spawns a file select dialog to choose a YAML style list of astronomical targets and associated gPhoton data products')
    if user_arguments: 
        args = parser.parse_args(user_arguments)
    else: 
        args = parser.parse_args()

    target_data_products = {}

    # If the user specified a gGui YAML file, load its targets
    if args.target_list:
        for file in args.target_list:
            target_list_path = str(pathlib.Path(file).absolute())
            target_data_products[target_list_path] = validate_targlist_format(yaml.load(open(target_list_path, 'r'), Loader=yaml.BaseLoader), target_list_path)
    # If the user requested a file-selector dialog to select a gGui YAML file, display it and load its contents
    if args.yaml_select:
        x = QtWidgets.QApplication([])
        for ggui_yaml_file in ggui_glue_application.prompt_user_for_file("Select GGUI YAML Target List", "gGUI YAML (*.yaml; *.yml)"):
            target_data_products[ggui_yaml_file] = validate_targlist_format(yaml.load(open(ggui_yaml_file, 'r'), Loader=yaml.BaseLoader), ggui_yaml_file)
    # If no targets were recognized, notify the user
    if not target_data_products:
        print("No yaml received. Starting empty gGui session...")
    # Initialize gGui with user-supplied targets, if any
    ggui_app = ggui_glue_application(imported_target_catalogs=target_data_products)
    # Start gGui
    ggui_app.start()

if __name__ == '__main__':
    main()
