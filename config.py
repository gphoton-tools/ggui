from glue.core import Data, DataCollection
from glue.core.data_factories import has_extension, load_data

from glue.viewers.scatter.qt import ScatterWidget

from glue.config import menubar_plugin

from gPhoton.gphoton_utils import read_lc as read_lc

from PyQt5.QtWidgets import QFileDialog

def fnPromptUserForfile(dialogCaption, dialogNameFilter):
    # Set File Dialog Options
    caption = dialogCaption
    dialog = QFileDialog(caption=caption)
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilter(dialogNameFilter)
    # Prompt User for file to import
    dialog.exec_()
    # Get array of File Names
    filenames = dialog.selectedFiles()
    return filenames

@menubar_plugin("Load gPhoton CSV Plot")
def my_plugin(session, dataLibrary):
    """
    Data loader customized for 'typical' gPhoton CSV Lightcurves, 
        specifically laoding t_mean and flux_bgsub

    This function extracts calibrated fluxes (flux_bgsub) and mean 
        timestamps (t_mean) and makes plot
    """

    # Prompt User via File Dialog for LightCurve CSVs
    lightcurveFilenames = fnPromptUserForfile("Select gPhoton CSV Lightcurve file", 
                                              "Lightcurve CSV (*.csv)")

    # Prompt User via File Dialog for CoAdd Fits
    coaddFilenames = fnPromptUserForfile("Select gPhoton FITS CoAdd file", 
                                              "CoAdd FITS (*.fits)")
    # Prompt User via File Dialog for Image Cube Fits
    cubeFilenames = fnPromptUserForfile("Select gPhoton FITS Image Cube file", 
                                              "Image Cube FITS (*.fits)")

    # Import Lightcurve CSVs to DataCollection
    for lightcurveFile in lightcurveFilenames:
        lightcurveData = load_data(lightcurveFile)
        dataLibrary.append(lightcurveData)
        # Generate 2D ScatterPlot Canvas for Lightcurve CSVs
        from glue.app.qt.application import GlueApplication
        glueApp = GlueApplication(dataLibrary)
        scatter = glueApp.new_data_viewer(ScatterWidget)
        scatter.add_data(lightcurveData)
        glueApp.start()
        

    # Import CoAdd Fits to DataCollection

    # Import Image Cube Fits to DataCollection


    
    

    # Generate 2D Image Viewer Canvas for CoAdd Fits

    # Generate 2D Image Viewer Canvas for Image Cube Fits

    return

    """
    dataArray = []

    # Read in CSV file using gPhoton.gphoton_utils.read_lc
    print(filename)
    csvRaw = read_lc(filename)

    # Create Data Object from glue using imported two columns from CSV
    csvData = Data(Flux_BackgroundSubtracted=csvRaw[['flux_bgsub']], MeanTime=csvRaw[['t_mean']], label='lightcurve') 

    # Return Array of Data
    dataArray.append(csvData)
    data_collection.append(csvData)
    #dc.append(load_data('cr_dra_lc.csv'))
    sw = ScatterWidget(session)
    sw.add_data(csvData)
    sw.register_to_hub()

    #return dataArray
    return

    """
