from glue.core import Data
from glue.config import data_factory
from glue.core.data_factories import has_extension

from gPhoton.gphoton_utils import read_lc as read_lc

@data_factory('gPhoton Lightcurve', has_extension('csv'), default='csv')
def gPhoton_data(filename):
    """
    Data loader customized for 'typical' gPhoton CSV Lightcurves, 
        specifically laoding t_mean and flux_bgsub

    This function extracts calibrated fluxes (flux_bgsub) and mean 
        timestamps (t_mean) and makes plot
    """
    dataArray = []

    # Read in CSV file using gPhoton.gphoton_utils.read_lc
    csvRaw = read_lc(filename)

    # Create Data Object from glue using imported two columns from CSV
    csvData = Data(time=csvRaw[['flux_bgsub']], flux=csvRaw[['t_mean']], label='lightcurve') 

    # Return Array of Data
    dataArray.append(csvData)
    return dataArray