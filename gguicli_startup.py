"""
.. module:: gguicli_startup
    :synopsis: Startup script to import gPhoton data products into Glue Data Visualizer
.. moduleauthor:: Duy Nguyen <dtn5ah@virginia.edu>
"""

from glue.core.data_factories import load_data
from glue.core import Data, DataCollection
from glue.core.link_helpers import LinkSame
from glue.app.qt.application import GlueApplication
from glue.config import settings

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

def create_scatter_canvas(dataToDisplay, xatt, yatt, glueApp):
    """
    Function to generate new scatter widget. (Designed for modularity and organization)

    :param dataToDisplay: Glue (Pandas) Data object to display on scatter widget
    :type dataToDisplay: glue.core.data.Data

    :param xatt: Index of Glue Data Object to display along x axis
    :type xatt: str

    :param yatt: Index of Glue Data Object to display along y axis
    :type yatt: str

    :param glueApp: Current instantiation of the Glue Application to spawn canvas into
    :type glueApp: glue.app.qt.application.GlueApplication
    """
    # Note for devs: Import inside function due to Glue Startup Script Workorder
    from glue.viewers.scatter.qt import ScatterWidget
    # Generate new scatter widget
    scatterCanvas = glueApp.new_data_viewer(ScatterWidget, dataToDisplay)
    # Set Scatter Canvas Attributes
    scatterCanvas.xatt = dataToDisplay.id[xatt]
    scatterCanvas.yatt = dataToDisplay.id[yatt]
    #glueApp.add_widget(scatterCanvas, "Test Label", 1)

def generateScatter():
    from glue.viewers.scatter.qt import ScatterWidget
    from glue.core.session import Session
    scatter = ScatterWidget()

def create_image_canvas(imageDataToDisplay, glueApp):
    """
    Function to generate a new image widget. (Designed for consistency with above)

    :param imageDataToDisplay: Glue (Pandas) Data object containing image intensity array
    :type imageDataToDisplay: glue.core.data.Data

    :param glueApp: Current instantiation of the Glue Application to spawn canvas into
    :type glueApp: glue.app.qt.application.GlueApplication
    """
    # Note for devs: Import inside function due to Glue Startup Script Workorder
    from glue.viewers.image.qt import ImageWidget
    # Generate new Image Widget
    glueApp.new_data_viewer(ImageWidget, imageDataToDisplay)

# ---------------------------- Begin main ---------------------------- #
# Initialize Glue Application with blank Data Collection
dataCollection = DataCollection()
glueApp = GlueApplication(dataCollection)
glueApp.new_tab()
tab = glueApp.tab_bar
#import ipdb; ipdb.set_trace()
#tab.setText("Testing")
#generateScatter()


lightcurveFilenames = []
coaddFilenames = []
cubeFilenames = []

# Prompt User via File Dialog for LightCurve CSVs
if settings.OPTION1 == True: 
    lightcurveFilenames = prompt_user_for_file("Select gPhoton CSV Lightcurve file",
                                               "Lightcurve CSV (*.csv)")
# Prompt User via File Dialog for CoAdd Fits
if settings.OPTION2 == True: 
    coaddFilenames = prompt_user_for_file("Select gPhoton FITS CoAdd file",
                                          "CoAdd FITS (*.fits)")
# Prompt User via File Dialog for Image Cube Fits
if settings.OPTION3 == True:
    cubeFilenames = prompt_user_for_file("Select gPhoton FITS Image Cube file",
                                         "Image Cube FITS (*.fits)")


# Import Lightcurve CSVs to DataCollection
for lightcurveFile in lightcurveFilenames:
    # Load Data from file. Add to current Data Collection
    csvData = load_data(lightcurveFile)
    dataCollection.append(csvData)
    # Cleanse raw csvData to only t_mean and flux_bgsub.
    # Add that data "subset" (not glue subset, just a subset) to Data Collection.
    # Must be in Data Collection to use
    lightcurveData = Data(Flux_BackgroundSubtracted=csvData['flux_bgsub'],
                          MeanTime=csvData['t_mean'],
                          label='Lightcurve of ' + lightcurveFile)
    dataCollection.append(lightcurveData)
    # Generate 2D ScatterPlot Canvas for Lightcurve CSVs
    create_scatter_canvas(lightcurveData, 'MeanTime',
                          'Flux_BackgroundSubtracted', glueApp)

# Import CoAdd Fits to DataCollection
for coaddFile in coaddFilenames:
    # Load Image from file
    fitsImage = load_data(coaddFile)
    #fitsImage['label'] = "CoAdd Image of " + coaddFile
    # Import Image to Data Collection for plotting
    dataCollection.append(fitsImage)
    # Generate 2D Image Viewer Canvas for coadd Images
    create_image_canvas(fitsImage, glueApp)

# Import Image Cube Fits to DataCollection
for cubeFile in cubeFilenames:
    # Load Image from file
    fitsImage = load_data(cubeFile)
    #fitsImage['label'] = "CoAdd Image of " + coaddFile
    # Import Image to Data Collection for plotting
    dataCollection.append(fitsImage)
    # Generate 2D Image Viewer Canvas for Image Cube Fits
    create_image_canvas(fitsImage, glueApp)


viewers = glueApp.viewers

#start Glue
glueApp.start()
