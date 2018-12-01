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

X_MONITOR_RES = 1080
WIN_OS_X_OFFSET = 145
x_glue_win_size = X_MONITOR_RES - WIN_OS_X_OFFSET

Y_MONITOR_RES = 1920
WIN_OS_Y_OFFSET = 320
y_glue_win_size = Y_MONITOR_RES - WIN_OS_Y_OFFSET

def create_scatter_canvas(dataToDisplay, x_att, y_att, glueApp, window_title=None, plot_title=None, x_min=None, x_max=None, x_window_size=None, y_window_size=None, x_window_pos=None, y_window_pos=None):
    """
    Function to generate new scatter widget. (Designed for modularity and organization)

    :param dataToDisplay: Glue (Pandas) Data object to display on scatter widget
    :type dataToDisplay: glue.core.data.Data

    :param xatt: Index of Glue Data Object to display along x axis
    :type xatt: str

    :param yatt: Index of Glue Data Object to display along y axis
    :type yatt: str

    :param plot_title: Title to be displayed on graph
    :type plot_tite: str
 
    :param xmin: Minimum value of X Axis
    :type xmin: numpy.float64

    :param xmax: Maximum value of X Axis
    :type xmax: numpy.float64

    :param glueApp: Current instantiation of the Glue Application to spawn canvas into
    :type glueApp: glue.app.qt.application.GlueApplication
    """
    # Note for devs: Import inside function due to Glue Startup Script Workorder
    from glue.viewers.scatter.qt import ScatterViewer
    sv = ScatterViewer(glueApp.session)
    sv.add_data(dataToDisplay)
    return sv
    # Generate new scatter widget
    scatterCanvas = glueApp.new_data_viewer(ScatterViewer, dataToDisplay)
    # Set Scatter Canvas Attributes
    if window_title: scatterCanvas.setWindowTitle(window_title)
    if plot_title: scatterCanvas.axes.set_title(plot_title)
    scatterCanvas.state.x_att = dataToDisplay.id[x_att]
    scatterCanvas.state.y_att = dataToDisplay.id[y_att]
    if x_min: scatterCanvas.state.x_min = x_min
    if x_max: scatterCanvas.state.x_max = x_max
    if x_window_size and y_window_size: scatterCanvas.viewer_size = x_window_size, y_window_size
    if x_window_pos and y_window_pos: scatterCanvas.position = x_window_pos, y_window_pos

    #scatterCanvas.position = 100,100
    #scatterCanvas.position = 100,100
    return scatterCanvas

def create_image_canvas(imageDataToDisplay, glueApp, window_title=None, plot_title=None, x_window_size=None, y_window_size=None, x_window_pos=None, y_window_pos=None):
    """
    Function to generate a new image widget. (Designed for consistency with above)

    :param imageDataToDisplay: Glue (Pandas) Data object containing image intensity array
    :type imageDataToDisplay: glue.core.data.Data

    :param glueApp: Current instantiation of the Glue Application to spawn canvas into
    :type glueApp: glue.app.qt.application.GlueApplication
    """
    # Note for devs: Import inside function due to Glue Startup Script Workorder
    from glue.viewers.image.qt import ImageViewer
    sv = ImageViewer(glueApp.session)
    sv.add_data(imageDataToDisplay)
    return sv
    
    # Generate new Image Widget
    imageCanvas = glueApp.new_data_viewer(ImageViewer, imageDataToDisplay)
    if window_title: imageCanvas.setWindowTitle(window_title)
    if plot_title: imageCanvas.axes.set_title(plot_title)
    if x_window_size and y_window_size: imageCanvas.viewer_size = x_window_size, y_window_size
    if x_window_pos and y_window_pos: imageCanvas.position = x_window_pos, y_window_pos
    return imageCanvas

def lightcurveChopList(parentData, axis, timeInterval):
    """
    Breaks observation data into observations separated by timeInterval. Returns list of times
    
    :param parentData: Glue (Pandas) Data Object containing CSV lightcurve data
    :type parentData: glue.core.data.Data

    :param axis: parameter to split across (usual = time)
    :type axis: string

    :param timeInterval: interval/amount to split parameter 'axis' across
    :type timeInterval: numpy.float64

    :returns: list -- List of autochop regions
    """
    import numpy
    # Calculate all time differences between points
    timeDifferences = numpy.diff(parentData[axis])
    # Find all indices of blank jumps greater than timeInterval
    obsWindows = []
    # Determine first observation window
    obsStart = parentData[axis, 0]
    for index, difference in enumerate(timeDifferences):
       # If the time difference is larger than specified time 
       if difference > timeInterval:
            # End time is the current index
            obsEnd = parentData['MeanTime', index]
            # Append this time window as tuple to master array
            obsWindows.append((index, obsStart, obsEnd))
            # Next window begins in next data point
            obsStart = parentData['MeanTime', index + 1]
    # Add last window to master array
    obsWindows.append((len(parentData[axis]), obsStart, parentData['MeanTime', -1]))
    return obsWindows

def lightcurveChopImport(glueApp, dataCollection, parentData, obsWindows):
    """
    Receives list of obs windows, breaks dataseries accordingly, imports data object to collection
    
    :param glueApp: Current instantiation of the Glue Application to spawn canvas into
    :type glueApp: glue.app.qt.application.GlueApplication

    :param dataCollection: Library of imported data objects to current Glue interface
    :type dataCollection: glue.core.data.DataCollection 

    :param parentData: Glue (Pandas) Data Object containing CSV lightcurve data
    :type parentData: glue.core.data.Data

    :param obsWindows: List of observation windows with indices upon which to chop
    :type obsWindows: list
    """
    from glue.core import Data
    # Set Initial Window start to index 0
    indxStart = 0
    # Get List of all extensions
    extensionList = parentData.component_ids()
    for window in obsWindows:
        # Grab ending index from list
        indxEnd = window[0]
        # Instantiate new Data Object container for the chop
        newChop = Data(label="AutoChop " + str(indxStart))
        for extension in extensionList:
            # Break every extension into segments defined by indxStart and indxEnd
            newChop[str(extension)] = parentData[extension][indxStart:indxEnd]
        # Import completed chop into dataCollection
        dataCollection.append(newChop)
        # Display Chop (for debugging purposes)
        #create_scatter_canvas(newChop,'MeanTime','Flux_BackgroundSubtracted',glueApp)
        # Move new index start to next index beyond current window
        indxStart = indxEnd + 1

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

def loadTarget(glueApp, fixedTab, dataCollection, targetName, targetFiles):
    """
    Given a specific 

    :returns: dict -- Dictionary of gGui Targets and corresponding file locations
    """
    def loadLightcurve(glueApp, fixedTab, dataCollection, targ_name, lcFileName):
        print(lcFileName)
        # Load Data from file. Add to current Data Collection
        csvData = load_data(lcFileName)
        dataCollection.append(csvData)
        # Cleanse raw csvData to only t_mean and flux_bgsub.
        # Add that data "subset" (not glue subset, just a subset) to Data Collection.
        # Must be in Data Collection to use
        lightcurveData = Data(Flux_BackgroundSubtracted=csvData['flux_bgsub'],
                            MeanTime=csvData['t_mean'],
                            label='Lightcurve of ' + lcFileName)
        dataCollection.append(lightcurveData)
        # AutoChop Lightcurve and import those chops
        obsWindows = lightcurveChopList(lightcurveData, "MeanTime", 3600)
        lightcurveChopImport(glueApp, dataCollection, lightcurveData, obsWindows)
        # Generate 2D ScatterPlot Canvas for Lightcurve CSVs and add to Glue
        lcWidget = create_scatter_canvas(lightcurveData, 
                            'MeanTime',
                            'Flux_BackgroundSubtracted', 
                            glueApp,
                            window_title=("Full Lightcurve of: " + lcFileName),
                            plot_title='Lightcurve of ' + targ_name,
                            x_window_size =   y_glue_win_size,
                            y_window_size =   floor(x_glue_win_size/3),
                            x_window_pos  =   1,
                            y_window_pos  =   1
        )
        fixedTab.loadLightcurve(lcWidget)

    def loadCoadd(glueApp, fixedTab, dataCollection, targ_name, coaddFileName):
        print(coaddFileName)
        # Load Image from file
        fitsImage = load_data(coaddFileName)
        # Import Image to Data Collection for plotting
        dataCollection.append(fitsImage)
        # Generate 2D Image Viewer Canvas for coadd Images
        caWidget = create_image_canvas(fitsImage, 
                            glueApp, 
                            window_title=('CoAdd Image of: ' + coaddFileName),
                            plot_title='CoAdd of ' + targ_name,
                            x_window_size   =   floor(y_glue_win_size/2),
                            y_window_size   =   floor(x_glue_win_size*(2.0/3.0)),
                            x_window_pos    =   1,
                            y_window_pos    =   floor(x_glue_win_size/3)
        )
        fixedTab.loadCoadd(caWidget)

    def loadCube(glueApp, fixedTab, dataCollection, targ_name, cubeFileName):
        print(cubeFileName)
        # Load Image from file
        fitsImage = load_data(cubeFileName)
        # Import Image to Data Collection for plotting
        dataCollection.append(fitsImage)
        # Generate 2D Image Viewer Canvas for Image Cube Fits
        cubeWidget = create_image_canvas(fitsImage,
                            glueApp,
                            window_title=('3D Image Cube of: ' + cubeFileName),
                            plot_title=('Cube of ' + targ_name + ': [' + str(datetime.datetime.now()) + ']'),
                            x_window_size   =   floor(y_glue_win_size/2),
                            y_window_size   =   floor(x_glue_win_size*(2.0/3.0)),
                            x_window_pos    =   floor(y_glue_win_size/2),
                            y_window_pos    =   floor(x_glue_win_size/3)
        )
        fixedTab.loadCube(cubeWidget)

    # Defines which function loads which datatype
    loadFunctions = {'lightcurve': loadLightcurve, 'coadd': loadCoadd, 'cube': loadCube}
    # For each target file, call its corresponding load function
    for dataProductType in targetFiles:
        #dataProductType, filePath = gGuiDataProductListing
        loadFunctions[dataProductType](glueApp, fixedTab, dataCollection, targetName, targetFiles[dataProductType])

def main():
    # Initialize Glue Application with blank Data Collection
    dataCollection = DataCollection()
    glueApp = GlueApplication(dataCollection)
    #glueApp.new_tab()
    tabBar = glueApp.tab_widget
    fixedTab=qtTabLayouts.overviewTabLayout()
    tabBar.addTab(fixedTab, "Overview Tab")
    tabBar.setCurrentWidget(fixedTab)
    fixedTab.subWindowActivated.connect(glueApp._update_viewer_in_focus)

    # Get list of targets from user
    gGuiTargetList = getGguiDataProducts()
    # Because we don't have a Multi-Target Manager yet, just choose the first one and load that one into gGui
    targNames = list(gGuiTargetList.keys()) 
    print(str(len(targNames)) + " targets received. Loading " + str(targNames[0]) + " as default.")
    loadTarget(glueApp, fixedTab, dataCollection, targNames[0], gGuiTargetList[targNames[0]])
    
    

    #glueApp.choose_new_fixed_layout_tab(qtTabLayouts.overviewTabLayout)
    
    #start Glue
    glueApp.start()

if __name__ == '__main__':
    main()
