"""
.. module:: autochop.py
    :synopsis: Determines time windows of GALEX observations based on time 
.. moduleauthor:: Duy Nguyen <dtn5ah@virginia.edu>
"""
import numpy
from glue.core import Data

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


# Before code restructuring, this was the only method here. Not sure what this is supposed to do in context of the other autochop methods...
def lightcurveChop(parentData, axis, timeInterval):
    
    # Calculate all time differences between points
    timeDifferences = numpy.diff(parentData[axis])
    # Find all indices of blank jumps greater than timeInterval
    obsWindows = []
    obsStart = parentData[axis, 0]
    for index, difference in enumerate(timeDifferences):
        if difference > timeInterval:
            obsEnd = parentData['MeanTime', index]
            obsWindows.append((obsStart,obsEnd))
            obsStart = parentData['MeanTime', index + 1]
    obsWindows.append((obsStart, parentData['MeanTime', -1]))

    return obsWindows
    """
    chopMeanTimes = []
    for chopIndex in chopIndices:
        chopMeanTimes.append(parentData['MeanTime',chopIndex])
    import ipdb; ipdb.set_trace()
    """

# Note for later. This is how you autochop :P
#from autochop import lightcurveChopList, lightcurveChopImport
#obsWindows = lightcurveChopList(lightcurveData, "MeanTime", 3600)
#lightcurveChopImport(glueApp, dataCollection, lightcurveData, obsWindows)