"""
.. module:: gguicli_startup
    :synopsis: Startup script to import gPhoton data products into Glue Data Visualizer
.. moduleauthor:: Duy Nguyen <dtn5ah@virginia.edu>
"""

# Note to Devs: Glue does not fully support upper imports. Imports must be done within functions
from glue.core.data_factories import load_data
from glue.core import DataCollection
from glue.core.link_helpers import LinkSame
from glue.app.qt.application import GlueApplication
from glue.config import settings
import yaml

import qtTabLayouts
from autochop import lightcurveChopList, lightcurveChopImport

from targetManager import targetManager

def main():
    # Initialize Glue Application with blank Data Collection
    dataCollection = DataCollection()
    glueApp = GlueApplication(dataCollection)
    # Save a reference to the default tab. We won't need this, but can't delete it until we have multiple tabs
    defaultTab = glueApp.current_tab

    targManager = targetManager()

    # Get list of targets from user
    def getGguiDataProducts():
        """
        Prompts user to load gGui Data Products

        :returns: dict -- Dictionary of gGui Targets and corresponding file locations
        """

        def prompt_user_for_file(dialogCaption, dialogNameFilter):
            """
            Modular QtWidget File-Selection Dialog to prompt user for file import.
                Returns array of filenames selected

            :param dialogCaption: Caption to display along top of file dialog window
            :type dialogCaption: str

            :param dialogNameFilter: Filters file dialog to certain extension
            :type dialogNameFilter: str

            :returns: list -- Python list of filenames selected by user
            """
            # Note for devs: Import inside function due to Glue Startup Script Workorder
            from qtpy.QtWidgets import QFileDialog # See GitHub Issue Ticket #7
            # Set File Dialog Options
            dialog = QFileDialog(caption=dialogCaption)
            dialog.setFileMode(QFileDialog.ExistingFiles)
            dialog.setNameFilter(dialogNameFilter)
            # Prompt User for file to import
            dialog.exec_()
            # Get array of File Names
            filenames = dialog.selectedFiles()
            return filenames

        ggui_load_format = input("Load type (y)aml or (m)anual: ")
        #ggui_load_format = 'd'
        if ggui_load_format == 'y':
            ggui_yaml = prompt_user_for_file("Select GGUI YAML Target List", "gGUI YAML (*.yaml; *.yml)")[0]
            targManager.loadGguiYaml(ggui_yaml)
        elif ggui_load_format == 'm':
            # Prompt User via File Dialog for LightCurve CSVs
            lightcurveFilenames = prompt_user_for_file("Select gPhoton CSV Lightcurve file", "Lightcurve CSV (*.csv)")[0]
            # Prompt User via File Dialog for CoAdd Fits
            coaddFilenames = prompt_user_for_file("Select gPhoton FITS CoAdd file", "CoAdd FITS (*.fits)")[0]
            # Prompt User via File Dialog for Image Cube Fits
            cubeFilenames = prompt_user_for_file("Select gPhoton FITS Image Cube file", "Image Cube FITS (*.fits)")[0]
            #return {"Target": {'lightcurve': lightcurveFilenames, 'coadd': coaddFilenames, 'cube': cubeFilenames}}
            targManager.loadTargetDict({"Target": {'lightcurve': lightcurveFilenames, 'coadd': coaddFilenames, 'cube': cubeFilenames}})
        elif ggui_load_format == 'd':
            targManager.loadGguiYaml('C:\\ggui\\dataProducts\\cr_dra_win.yaml')
        else:
            print("Unrecognized character")
            exit(-1)
    getGguiDataProducts()
    # Because we don't have a Multi-Target Manager yet, just choose the first one and load that one into gGui
    targNames = list(targManager.getTargetNames())
    targManager.setPrimaryTarget(targNames[0])
    print(str(len(targNames)) + " targets received. Loading " + str(targNames[0]) + " as default.")
    
    # Create Overview Tab using target manager's primary target
    fixedTab = qtTabLayouts.overviewTabLayout(session=glueApp.session, targName=targNames[0], targData=targManager.getPrimaryData())
    glueApp.tab_widget.addTab(fixedTab, "Overview of " + str(targNames[0]))
    # Set Overview Tab to focus
    glueApp.tab_widget.setCurrentWidget(fixedTab)
    fixedTab.subWindowActivated.connect(glueApp._update_viewer_in_focus)
    
    # Note for later. This is how you autochop :P
    #obsWindows = lightcurveChopList(lightcurveData, "MeanTime", 3600)
    #lightcurveChopImport(glueApp, dataCollection, lightcurveData, obsWindows)

    # Delete first default tab
    glueApp.close_tab(glueApp.get_tab_index(defaultTab), False)
    
    #start Glue
    glueApp.start()

if __name__ == '__main__':
    main()
