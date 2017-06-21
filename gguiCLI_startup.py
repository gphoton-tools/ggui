from glue.core.data_factories import load_data
from glue.core import Data, DataCollection
from glue.core.link_helpers import LinkSame
from glue.app.qt.application import GlueApplication

def fnPromptUserForfile(dialogCaption, dialogNameFilter):
    from qtpy.QtWidgets import QFileDialog # See Issue Ticket #7
    # Set File Dialog Options
    caption = dialogCaption
    dialog = QFileDialog(caption=caption)
    dialog.setFileMode(QFileDialog.ExistingFiles)
    dialog.setNameFilter(dialogNameFilter)
    # Prompt User for file to import
    dialog.exec_()
    # Get array of File Names
    filenames = dialog.selectedFiles()
    return filenames

def fnCreateNewScatterCanvas(dataCollection, dataToDisplay, xatt, yatt, glueApp):
    from glue.viewers.scatter.qt import ScatterWidget
    # Generate new scatter widget
    scatterCanvas = glueApp.new_data_viewer(ScatterWidget)
    # Import scatter dataset
    scatterCanvas.add_data(dataToDisplay)
    scatterCanvas.xatt = dataToDisplay.id[xatt]
    scatterCanvas.yatt = dataToDisplay.id[yatt]
    # Specify Misc. Scatterplot Attributes

def fnRenderImage(datacollection, imageDataToDisplay, glueApp):
    from glue.viewers.image.qt import ImageWidget
    # Generate new Image Widget
    imageCanvas = glueApp.new_data_viewer(ImageWidget)
    # Import image dataset
    imageCanvas.add_Data(imageDataToDisplay)

# Initialize Glue Application with blank Data Collection
dataCollection = DataCollection()
glueApp = GlueApplication(dataCollection)

# Prompt User via File Dialog for LightCurve CSVs
lightcurveFilenames = fnPromptUserForfile("Select gPhoton CSV Lightcurve file", "Lightcurve CSV (*.csv)")
# Prompt User via File Dialog for CoAdd Fits
coaddFilenames = fnPromptUserForfile("Select gPhoton FITS CoAdd file", "CoAdd FITS (*.fits)")
# Prompt User via File Dialog for Image Cube Fits
cubeFilenames = fnPromptUserForfile("Select gPhoton FITS Image Cube file", "Image Cube FITS (*.fits)")

# Import Lightcurve CSVs to DataCollection
for lightcurveFile in lightcurveFilenames:
    # Load Data from file. Add to current Data Collection
    csvData = load_data(lightcurveFile)
    #dataCollection.append(csvData)
    # Cleanse raw csvData to only t_mean and flux_bgsub.
    # Add that data "subset" (not glue subset, just a subset) to Data Collection. Must be in Data Collection to use
    lightcurveData = Data(Flux_BackgroundSubtracted=csvData['flux_bgsub'], 
                            MeanTime=csvData['t_mean'], 
                            label='Lightcurve of ' + lightcurveFile)
    dataCollection.append(lightcurveData)
    # Generate 2D ScatterPlot Canvas for Lightcurve CSVs
    fnCreateNewScatterCanvas(dataCollection, lightcurveData, 'MeanTime', 'Flux_BackgroundSubtracted', glueApp)

# Import CoAdd Fits to DataCollection
for coaddFile in coaddFilenames:
    # Load Image from file
    fitsImage = load_data(coaddFile)
    # Import Image to Data Collection for plotting
    dataCollection.append(fitsImage)
    # Generate 2D Image Viewer Canvas for coadd Images
    fnRenderImage(dataCollection, fitsImage, glueApp)


# Import Image Cube Fits to DataCollection

# Generate 2D Image Viewer Canvas for CoAdd Fits

# Generate 2D Image Viewer Canvas for Image Cube Fits

#start Glue
glueApp.start()