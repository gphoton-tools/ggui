"""
.. module:: mastCrossSearch
    :synopsis: Search MAST Archive for matching observations on a given gPhoton GALEX WCS frame
.. moduleauthor:: Duy Nguyen <dtn5ah@virginia.edu>
"""
# Science Imports
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import pixel_to_skycoord as pix2RaDec
from math import floor
from scipy.spatial import distance

# API Response Imports
import sys
import json
try: # Python 3.x
    from urllib.parse import quote as urlencode
    from urllib.request import urlretrieve
except ImportError:  # Python 2.x
    from urllib import pathname2url as urlencode
    from urllib import urlretrieve
try: # Python 3.x
    import http.client as httplib 
except ImportError:  # Python 2.x
    import httplib 

#TEMPFILE = 'cr_dra_count_coadd.fits'
TEMPFILE = 'Messier060_coadd.fits'


def getFITSCornerCoords(filename):
    fitsImage = fits.open(filename)
    wcs = WCS(fitsImage[0].header)
    rangeX = fitsImage[0].header['NAXIS1']
    rangeY = fitsImage[0].header['NAXIS2']
    corner1 = pix2RaDec(rangeX, 0, wcs)
    corner2 = pix2RaDec(0, 0, wcs)
    corner3 = pix2RaDec(0, rangeY, wcs)
    corner4 = pix2RaDec(rangeX, rangeY, wcs)
    cornerCoords = [corner1, corner2, corner3, corner4]
    return cornerCoords

def getFITSCenterCoords(filename):
    fitsImage = fits.open(filename)
    wcs = WCS(fitsImage[0].header)
    rangeX = fitsImage[0].header['NAXIS1']
    rangeY = fitsImage[0].header['NAXIS2']
    center = pix2RaDec(floor(rangeX / 2.0), floor(rangeY / 2.0), wcs)
    return center

def minCircle(cornerList, center):
    radius = distance.euclidean((cornerList[0].ra.degree, cornerList[0].dec.degree),(center.ra.degree, center.dec.degree))
    return radius

def mastConeQuery(center, radius):
    # Define target server
    server = 'mast.stsci.edu'
    requestsVersion = ".".join(map(str, sys.version_info[:3]))

    # Define request parameters
    requestParams = {'service':'Mast.Caom.Cone',
                     'params':{'ra':center.ra.degree,
                               'dec':center.dec.degree,
                               'radius':radius},
                     'format':'json',
                     'pagesize':2000,
                     'removenullcolumns':True,
                     'timeout':30,
                     'removecache':True}
    JSONquery = urlencode(json.dumps(requestParams))

    # Define HTTP parameters
    httpHeaders = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain",
                   "User-agent":"python-requests/" + requestsVersion}

    # Connect to Server
    connMAST = httplib.HTTPSConnection(server)
    # Invoke MAST Request
    connMAST.request("POST", "/api/v0/invoke", "request="+JSONquery, httpHeaders)
    # Receive MAST Response
    httpResponse = connMAST.getresponse()
    # Return HTTP Response objects
    header = httpResponse.getheaders()
    data = httpResponse.read().decode('utf-8')
    return header,data

def extractGGUIFields(jsonReturn):
    gguiFields = []
    for i, obs in enumerate(jsonReturn['data']):
        mission = obs['obs_collection']
        project = obs['project']
        region = obs['s_region']
        dataType = obs['dataproduct_type']
        gguiFields.append((i, mission, project, dataType, region))
        #print(i, "\t", mission, "\t", project, "\t", dataType, "\n\t\t", region)
    return gguiFields

def appendRegionList(regOutFile, regionParse, paramIgnore):
    shape = regionParse[0]
    ds9Region = regionParse[0].lower() + "("
    #import ipdb; ipdb.set_trace()
    for param in regionParse[paramIgnore:]:
        ds9Region = ds9Region + param + ", "
    ds9Region = ds9Region[:-2] + ")"
    print(ds9Region)

    # DS9 Style Arguments
    mission = obs['obs_collection']
    project = obs['project']
    #import ipdb; ipdb.set_trace()
    if type(project) is type(None): project = "NULL"
    styleArgs = ' ' + '#'
    if project[:4] == "hlsp":
        styleArgs = styleArgs + ' ' + "color=yellow"
    elif mission == "HST" or mission == "HLA":
        styleArgs = styleArgs + ' ' + "color=red"
    elif mission == "KEPLER" or mission == "K2":
        styleArgs = styleArgs + ' ' + "color=green"
    elif mission == "PS1":
        styleArgs = styleArgs + ' ' + "color=blue"
    elif mission == "SWIFT":
        styleArgs = styleArgs + ' ' + "color=cyan"
    elif mission == "GALEX":
        styleArgs = styleArgs + ' ' + "color=magenta"
    else:
        styleArgs = styleArgs + ' ' + "color=green dash=1"
    ds9Region = ds9Region + styleArgs
    print(ds9Region)
    regOutFile.write(ds9Region + "\n")
    

def exportDS9Regions(jsonReturn, fileOutputName):
    gguiFields = []
    regOutFile = open(fileOutputName, "w")

    # DS9 Geometry Syntax
    for i, obs in enumerate(jsonReturn['data']):
        region = obs['s_region']
        regionParse = region.split()
        ds9Region = ''
        paramIgnore = 0
        for param in regionParse:
            try:
                float(param)
                break
            except Exception: paramIgnore+=1; pass
        if regionParse[0] != "CIRCLE" and regionParse[0] != "POLYGON":
            print("Illegal/Unimplemented Shape Detected: ", regionParse[0], ". Skipping Object")
        else:
            #appendRegionList(regOutFile, regionParse, paramIgnore)
            shape = regionParse[0]
            ds9Region = regionParse[0].lower() + "("
            #import ipdb; ipdb.set_trace()
            for param in regionParse[paramIgnore:]:
                ds9Region = ds9Region + param + ", "
            ds9Region = ds9Region[:-2] + ")"
            print(ds9Region)

            # DS9 Style Arguments
            mission = obs['obs_collection']
            project = obs['project']
            #import ipdb; ipdb.set_trace()
            if type(project) is type(None): project = "NULL"
            styleArgs = ' ' + '#'
            if project[:4] == "hlsp":
                styleArgs = styleArgs + ' ' + "color=yellow"
            elif mission == "HST" or mission == "HLA":
                styleArgs = styleArgs + ' ' + "color=red"
            elif mission == "KEPLER" or mission == "K2":
                styleArgs = styleArgs + ' ' + "color=green"
            elif mission == "PS1":
                styleArgs = styleArgs + ' ' + "color=blue"
            elif mission == "SWIFT":
                styleArgs = styleArgs + ' ' + "color=cyan"
            elif mission == "GALEX":
                styleArgs = styleArgs + ' ' + "color=magenta"
            else:
                styleArgs = styleArgs + ' ' + "color=green dash=1"
            ds9Region = ds9Region + styleArgs
            print(ds9Region)
            regOutFile.write(ds9Region + "\n")
    regOutFile.close()
            
# Get Coordinates of Corners
cornerCoords = getFITSCornerCoords(TEMPFILE)
# Get Coordinates of Frame Center
center = getFITSCenterCoords(TEMPFILE)
# Get Radius of smallest enclosing circle of frame
radius = minCircle(cornerCoords, center)

# Perform Mast Cone Query; interpret results
header,data = mastConeQuery(center, radius)
jsonReturn = json.loads(data)
# Extract Relevant information from return
gguiFields = extractGGUIFields(jsonReturn)
#print(gguiFields)
exportDS9Regions(jsonReturn, TEMPFILE + ".reg")
