# Plugin Imports
from qtpy.QtWidgets import QFileDialog # See Issue Ticket #7

from glue.core import Data, DataCollection
from glue.core.data_factories import has_extension, load_data
from glue.core import application_base

from glue.viewers.scatter.qt import ScatterWidget

from glue.config import menubar_plugin

from gPhoton.gphoton_utils import read_lc as read_lc

# Preferences Imports
from glue.config import settings, preference_panes
#from glue.external.qt import QtGui
from qtpy import QtGui

def fnPromptUserForfile(dialogCaption, dialogNameFilter):
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

def fnCreateNewScatterCanvas(dataCollection, dataToDisplay, glueApp):
    # Generate new scatter widget
    scatter = glueApp.new_data_viewer(ScatterWidget)
    # Specify new scatter widget
    scatter.add_data(dataToDisplay)
    scatter.xatt = dataToDisplay.id['MeanTime']
    scatter.yatt = dataToDisplay.id['Flux_BackgroundSubtracted']
    # Start Glue App containing 2D Scatter Canvas
    
    """
    self = application_base.Application()
    scatter = self.new_data_viewer(ScatterWidget)
    self.add_widget(scatter)
    """
@menubar_plugin("gPhoton++ Analysis Package")
def ggui_plugin(session, dataLibrary):
    """
    Data loader customized for 'typical' gPhoton CSV Lightcurves, 
        specifically laoding t_mean and flux_bgsub

    This function extracts calibrated fluxes (flux_bgsub) and mean 
        timestamps (t_mean) and makes plot
    """
    # Now that Glue has loaded, grab current instance of GlueApplication UI 
    # (ENV context has been defined)
    from glue.app.qt.application import GlueApplication
    
    # Generate new Glue GUI Window
    glueApp = GlueApplication(dataLibrary)

    
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
        # Load Data from file. Add to current Data Collection
        csvData = load_data(lightcurveFile)
        dataLibrary.append(csvData)
        # Cleanse raw csvData to only t_mean and flux_bgsub.
        # Add that data "subset" (not glue subset, just a subset) to Data Collection. Must be in Data Collection to use
        lightcurveData = Data(Flux_BackgroundSubtracted=csvData['flux_bgsub'], 
                              MeanTime=csvData['t_mean'], 
                              label=lightcurveFile)
        dataLibrary.append(lightcurveData)
        # Generate 2D ScatterPlot Canvas for Lightcurve CSVs
        fnCreateNewScatterCanvas(dataLibrary, lightcurveData, glueApp)

   
    # Import CoAdd Fits to DataCollection

    # Import Image Cube Fits to DataCollection

    # Generate 2D Image Viewer Canvas for CoAdd Fits

    # Generate 2D Image Viewer Canvas for Image Cube Fits

    # Start new Glue GUI with plots
    glueApp.start()
    
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

class MyPreferences():
        def __init__(self, parent=None):
            super(MyPreferences, self).__init__()
            #self.layout = QtGui.QFormLayout()
            
            self.option1 = QtGui.QCheckBox()
            self.layout.addRow("Prompt for Lightcurve CSVs")

            self.setLayout(self.layout)

            self.option1.setChecked(settings.OPTION1)

        def finalize(self):
            settings.OPTION1 = self.option1.isChecked()

settings.add('OPTION1', False, bool)
preference_panes.add('gPhoton++ Preferences', MyPreferences)