"""
.. module:: ggui
    :synopsis: Defines the gGui class and startup behavior
.. moduleauthor:: Duy Nguyen <dnguyen@nrao.edu>
"""

import argparse
import pathlib
import tempfile
import urllib
from urllib.parse import urlparse
import webbrowser
import yaml
from zipfile import ZipFile

from glue.core import DataCollection
from glue.app.qt.application import GlueApplication
from glue.config import menubar_plugin
from glue.utils import nonpartial
from PyQt5 import QtWidgets, QtCore

from ggui import qtTabLayouts
from ggui.targetManager import TargetManager
from ggui.make_param import validate_target_catalog_file
from .version import __version__

# Enable High DPI
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

class gGuiGlueApplication(GlueApplication):
    """Primary gGui Application Class
    Integrates gGui framework (target manager, custom tab generation, etc.) into Glue
    """

    def __init__(
        self,
        data_collection: DataCollection = DataCollection(),
        imported_target_catalogs: dict = None,
    ):
        """Initializes gGui
        If provided a dictionary of targets, in outlined gGui YAML structure,
        it will load those targets into the target manager

        :param data_collection: Glue data collection containing Glue data to plot
        :param imported_target_catalogs: Dict of targets and paths to associated gPhoton data products to load initially
        """
        super().__init__(data_collection)
        # Modify window title to specify gGui modified Glue environment
        self.setWindowTitle("gGui: gPhoton Graphical User Interface")
        # Add gGui YAML loader to "File" Menu
        self.menuBar().actions()[0].menu().addSeparator()
        self.menuBar().actions()[0].menu().addAction(
            "Load gGui Target Catalog", self.load_ggui_yaml
        )

        # Rename Glue "Help" to "Glue Help"
        self.menuBar().actions()[6].setText("&Glue Help")

        # Add "gGui Help" Menu
        menu_about_ggui = self.menuBar().addMenu("&gGui Help")
        # Add link to gGui ReadTheDocs
        ggui_rtd = QtWidgets.QAction("gGui &Online Documentation", menu_about_ggui)
        ggui_rtd.triggered.connect(
            nonpartial(webbrowser.open, "https://ggui.readthedocs.io/")
        )
        menu_about_ggui.addAction(ggui_rtd)
        # Add basic About information
        menu_about_ggui.addAction("About gGui", self.show_about_ggui)
        # Add tutorial button
        menu_about_ggui.addAction("Load gGui Sample Data", self.ggui_tutorial)

        # Save a reference to the default tab
        # We won't need this, but can't delete it until we have multiple tabs
        default_tab = self.current_tab

        # Initialize blank overview tab
        def init_overview_tab(self):
            # Initialize blank overview_widget
            self.overview_widget = qtTabLayouts.ggui_overview_tab(session=self.session)
            self.tab_widget.addTab(
                self.overview_widget, "gGui Overview Tab: No Data Loaded"
            )
            # Set Overview Tab to focus
            self.tab_widget.setCurrentWidget(self.overview_widget)

        init_overview_tab(self)

        # Initialize empty Target Manager
        self.target_manager = TargetManager(self, self.primary_target_changed)
        self.addToolBarBreak()
        self.addToolBar(self.target_manager)

        if imported_target_catalogs:
            # Load supplied target catalog into target manager
            # NOTE: Upon first load, Target Manager will automatically update target manager's
            #       primary target with the first entry in this dict.
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
        self.overview_widget.load_data(
            self.session,
            self.target_manager.getPrimaryName(),
            self.target_manager.getPrimaryData(),
        )
        self.tab_widget.setTabText(
            self.get_tab_index(self.overview_widget),
            "Overview of " + str(self.target_manager.getPrimaryName()),
        )

    def load_targets(self, imported_target_catalogs: dict):
        """
        Imports gGui-compliant data (see yaml standard) into target manager

        :param imported_target_catalogs: Dict of gGui yamls and filenames imported from main
        """
        for filename in imported_target_catalogs:
            self.target_manager.loadTargetDict(
                filename,
                imported_target_catalogs[filename]
            )

    def load_ggui_yaml(self):
        """Prompts user with File Dialog for gGui YAML Target List
        Validates the YAML file and loads it into the Target Manager
        """
        for ggui_yaml_file in gGuiGlueApplication.prompt_user_for_file(
            "Select GGUI YAML Target List", "gGUI YAML (*.yaml; *.yml)"
        ):
            self.target_manager.loadTargetDict(
                ggui_yaml_file, 
                validate_targlist_format(
                    yaml.load(open(ggui_yaml_file, "r"), Loader=yaml.BaseLoader),
                    ggui_yaml_file,
                )
            )

    def show_about_ggui(self):
        """Displays about gGui Message Box"""
        QtWidgets.QMessageBox.about(
            self,
            "About gGui",
            "gPhoton Graphical User Interface (gGui)\n"
            "Developed by Duy Nguyen, Scott Fleming\nVersion: "
            + __version__
            + "\n\ngGui is provided under the AURA Software License. "
            "Please see the included license for details.",
        )

    def ggui_tutorial(self):
        """Loads gGui sample data"""
        sample_data_url = 'https://github.com/gphoton-tools/ggui/raw/master/docs/ggui_tutorial_data2019-11-11.zip'
        # Dynamically get the sample data archive filename in case it changes
        sample_filename = pathlib.Path(urlparse(sample_data_url).path).name
        # Get temp path on disk to where this sample data will be written
        sample_data_local_path = pathlib.Path(tempfile.gettempdir()) / sample_filename

        # If we don't have the sample data downloaded, download it
        if not sample_data_local_path.is_file():
            print("Downloading sample data to: " + str(sample_data_local_path) + " from: " + str(sample_data_url))
            urllib.request.urlretrieve(sample_data_url, str(sample_data_local_path))
            print("Download Successful: " + str(sample_data_local_path.is_file()))

        with ZipFile(sample_data_local_path, 'r') as sample_data_zip:
            # Unzip sample data archive
            sample_data_zip.extractall(tempfile.gettempdir())
            # Resolve the yaml path and load it to gGui
            resolved_path = (pathlib.Path(tempfile.gettempdir()) / 'tutorial.yaml').resolve()
            self.load_targets({resolved_path: validate_target_catalog_file(str(resolved_path))})

    @staticmethod
    def prompt_user_for_file(dialog_caption: str, dialog_name_filter: str) -> list:
        """
        Modular QtWidget File-Selection Dialog to prompt user for file import.
        Returns array of filenames selected

        :param dialog_caption: Caption to display along top of file dialog window
        :param dialog_name_filter: Filters file dialog to certain extension
        """
        # Set File Dialog Options
        dialog = QtWidgets.QFileDialog(caption=dialog_caption)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        dialog.setNameFilter(dialog_name_filter)
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
    parser = argparse.ArgumentParser(
        description="gPhoton Graphical User Interface. An analysis package for GALEX gPhoton "
                    "data products"
    )
    parser.add_argument(
        "--target_list",
        nargs="+",
        help="Specify a path to a YAML style list of astronomical targets and associated gPhoton "
             "data products",
    )
    parser.add_argument(
        "--yaml_select",
        action="store_true",
        help="Spawns a file select dialog to choose a YAML style list of astronomical targets and "
             "associated gPhoton data products",
    )
    if user_arguments:
        args = parser.parse_args(user_arguments)
    else:
        args = parser.parse_args()

    target_data_products = {}

    # If the user specified a gGui YAML file, load its targets
    if args.target_list:
        for ggui_yaml_file in args.target_list:
            resolved_path = pathlib.Path(ggui_yaml_file).resolve()
            target_data_products[resolved_path] = validate_target_catalog_file(str(resolved_path))
    # If the user requested a file-selector dialog to select a gGui YAML file, display it and load
    #   its contents
    if args.yaml_select:
        x = QtWidgets.QApplication([])
        for ggui_yaml_file in gGuiGlueApplication.prompt_user_for_file(
            "Select GGUI YAML Target List", "gGUI YAML (*.yaml; *.yml)"
        ):
            resolved_path = pathlib.Path(ggui_yaml_file).resolve()
            target_data_products[resolved_path] = validate_target_catalog_file(str(resolved_path))
    # If no targets were recognized, notify the user
    if not target_data_products:
        print("No yaml received. Starting empty gGui session...")
    # Initialize gGui with user-supplied targets, if any
    ggui_app = gGuiGlueApplication(imported_target_catalogs=target_data_products)
    # Start gGui
    ggui_app.start()


if __name__ == "__main__":
    main()
