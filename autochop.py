"""
.. module:: autochop.py
    :synopsis: Determines time windows of GALEX observations based on time 
.. moduleauthor:: Duy Nguyen <dtn5ah@virginia.edu>
"""
import numpy
from glue.core import Data

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