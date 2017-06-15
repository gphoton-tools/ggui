from glue.core import Data, DataCollection
from glue.core.data_factories import has_extension, load_data
#from glue.app.qt.application import GlueApplication
from glue.viewers.scatter.qt import ScatterWidget

from glue.config import menubar_plugin

from gPhoton.gphoton_utils import read_lc as read_lc

from PyQt5.QtWidgets import QFileDialog

@menubar_plugin("Load gPhoton CSV Plot")
def my_plugin(session, data_collection):
    """
    Data loader customized for 'typical' gPhoton CSV Lightcurves, 
        specifically laoding t_mean and flux_bgsub

    This function extracts calibrated fluxes (flux_bgsub) and mean 
        timestamps (t_mean) and makes plot
    """

    # Prompt User via File Dialog for LightCurve CSVs

    # Prompt User via File Dialog for CoAdd Fits

    # Prompt User via File Dialog for Image Cube Fits


    # Import Lightcurve CSVs to DataCollection()

    # Import CoAdd Fits to DataCollection()

    # Import Image Cube Fits to DataCollection()


    # Generate 2D ScatterPlot Canvas for Lightcurve CSVs

    # Generate 2D Image Viewer Canvas for CoAdd Fits

    # Generate 2D Image Viewer Canvas for Image Cube Fits

    return

    """
    # Set File Dialog Options
    caption = ("Select gPhoton CSV Lightcurve file")
    dialog = QFileDialog(caption=caption)
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilter("Lightcurve CSV (*.csv)")

    # Prompt User for file to import
    dialog.exec_()

    # Get File Name (Need to grab first file name)
    filename = dialog.selectedFiles()[0]
    
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
