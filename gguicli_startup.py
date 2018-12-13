"""
.. module:: gguicli_startup
    :synopsis: Startup script to import gPhoton data products into Glue Data Visualizer
.. moduleauthor:: Duy Nguyen <dtn5ah@virginia.edu>
"""

# Note to Devs: Glue does not fully support upper imports. Imports must be done within functions
from glue.core.data_factories import load_data
from glue.core import Data, DataCollection
from glue.core.link_helpers import LinkSame
from glue.app.qt.application import GlueApplication
from glue.config import settings
from math import floor
import yaml
import datetime

import qtTabLayouts
from autochop import lightcurveChopList, lightcurveChopImport

def main():
    # Initialize Glue Application with blank Data Collection
    dataCollection = DataCollection()
    glueApp = GlueApplication(dataCollection)
    # Save a reference to the default tab. We won't need this, but can't delete it until we have multiple tabs
    defaultTab = glueApp.current_tab
    #glueApp.new_tab()

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
            ggui_yaml = prompt_user_for_file("Select GGUI YAML Target List", "gGUI YAML (*.yaml)")[0]
            with open(ggui_yaml, 'r') as f:
                return yaml.load(f)
                '''
                for targ_name, files in targ_dict.items():
                    targetNames.append(targ_name)
                    lightcurveFilenames.append((targ_name, files['lightcurve']))
                    coaddFilenames.append((targ_name, files['coadd']))
                    cubeFilenames.append((targ_name, files['cube']))
                '''
        elif ggui_load_format == 'm':
            
            
            # Prompt User via File Dialog for LightCurve CSVs
            if settings.OPTION1 == True: 
                lightcurveFilenames = prompt_user_for_file("Select gPhoton CSV Lightcurve file", "Lightcurve CSV (*.csv)")[0]
            # Prompt User via File Dialog for CoAdd Fits
            if settings.OPTION2 == True: 
                coaddFilenames = prompt_user_for_file("Select gPhoton FITS CoAdd file", "CoAdd FITS (*.fits)")[0]
            # Prompt User via File Dialog for Image Cube Fits
            if settings.OPTION3 == True:
                cubeFilenames = prompt_user_for_file("Select gPhoton FITS Image Cube file", "Image Cube FITS (*.fits)")[0]

            return {"Target": {'lightcurve': lightcurveFilenames, 'coadd': coaddFilenames, 'cube': cubeFilenames}}
        elif ggui_load_format == 'd':
            with open('C:\\ggui\\dataProducts\\cr_dra_win.yaml', 'r') as f:
                return yaml.load(f)
                '''
                for targ_name, files in targ_dict.items():
                    lightcurveFilenames.append((targ_name, files['lightcurve']))
                    coaddFilenames.append((targ_name, files['coadd']))
                    cubeFilenames.append((targ_name, files['cube']))
                '''
        else:
            print("Unrecognized character")
            exit(-1)
    gGuiTargetList = getGguiDataProducts()
    # Because we don't have a Multi-Target Manager yet, just choose the first one and load that one into gGui
    targNames = list(gGuiTargetList.keys()) 
    print(str(len(targNames)) + " targets received. Loading " + str(targNames[0]) + " as default.")
    
    #loadTarget(glueApp, fixedTab, dataCollection, targNames[0], gGuiTargetList[targNames[0]])
    def extractTargetData(targetFiles):
        print("Extracting target data")
        dataDict = {}
        for dataProductType in targetFiles:
            dataDict[dataProductType] = load_data(targetFiles[dataProductType])
        return dataDict
    targData = extractTargetData(gGuiTargetList[targNames[0]])
    
    tabBar = glueApp.tab_widget
    fixedTab=qtTabLayouts.overviewTabLayout(session=glueApp.session, targName=targNames[0], targData=targData)
    tabBar.addTab(fixedTab, "Overview of " + str(targNames[0]))
    #glueApp.close_tab(0, False)
    tabBar.setCurrentWidget(fixedTab)
    fixedTab.subWindowActivated.connect(glueApp._update_viewer_in_focus)
    
    #fixedTab.tileSubWindows()
    #print("###: " + str(fixedTab.activeSubWindow()))
    
    # Note for later. This is how you autochop :P
    #obsWindows = lightcurveChopList(lightcurveData, "MeanTime", 3600)
    #lightcurveChopImport(glueApp, dataCollection, lightcurveData, obsWindows)

    # Delete first default tab
    glueApp.close_tab(glueApp.get_tab_index(defaultTab), False)
    
    #start Glue
    glueApp.start()

if __name__ == '__main__':
    main()
