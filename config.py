from glue.core import Data
from glue.core.data_factories import has_extension
from glue.app.qt.application import GlueApplication

from glue.config import data_factory, importer, menubar_plugin

from gPhoton.gphoton_utils import read_lc as read_lc

from PyQt5.QtWidgets import QFileDialog

#@data_factory('gPhoton Lightcurve', has_extension('csv'), default='csv')
#def gPhoton_data(filename):

@importer("gPhoton Lightcurve Importer")
def gPhoton_data():

#@menubar_plugin("Load gPhoton CSV Plot")
#def my_plugin(session, data_collection):
    """
    Data loader customized for 'typical' gPhoton CSV Lightcurves, 
        specifically laoding t_mean and flux_bgsub

    This function extracts calibrated fluxes (flux_bgsub) and mean 
        timestamps (t_mean) and makes plot
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

    return dataArray



