"""
.. module:: qtTabLayouts
    :synopsis: Defines the gGui overview tab and associated tools
.. moduleauthor:: Duy Nguyen <dnguyen@nrao.edu>
"""

from configparser import ConfigParser
from PyQt5 import QtWidgets
from glue.app.qt.application import GlueApplication
import glue.core.session
from glue.config import qt_fixed_layout_tab, viewer_tool
from glue.viewers.common.qt.tool import Tool

from glue.viewers.matplotlib.qt.data_viewer import MatplotlibDataViewer
from glue.viewers.scatter.qt import ScatterViewer
from glue.viewers.image.qt import ImageViewer

from pkg_resources import resource_filename

class ggui_overview_base_viewer(MatplotlibDataViewer):
    """Base class for gGui data viewers
    Implements basic data import logic, band organizing, and UI methods
    Adds FUV/NUV band support and associated band toggle tools
    """
    tools = ['fuv_toggle', 'nuv_toggle', 'focus']
    
    def __init__(self, glue_session: glue.core.session, data: dict):
        """Initializes base gGui data viewer

        :param session: Corresponding Glue parent's 'session' object that stores 
        information about the current environment of glue. Needed for superclass constructor
        :param data: Band separated dict of data to load
        """
        super().__init__(glue_session)
        # Initialize internal cache to hold viewer's data for easy 'band-wise' access
        self.data_cache = {}
        for band, band_data in data.items():
            # Import data into data viewer
            self.add_data(band_data)
            # Find associated data layer created for that data and cache it along with the data
            # Have to currently loop through all layers and check if the data is the same as the 
            # one we're currently processing EVERY TIME. Horrible performance. Go back and fix!
            for index, layerData in enumerate([layers.layer for layers in self.state.layers]):
                if layerData == band_data:
                    self.data_cache[band] = {'data': band_data, 'layer': self.state.layers[index]}
                    break
        # Associate FUV datasets with the color blue, and NUV datasets with the color red
        if 'FUV' in self.data_cache:
            self.data_cache['FUV']['layer'].color = 'blue'
        if 'NUV' in self.data_cache:
            self.data_cache['NUV']['layer'].color = 'red'
        
    def toggle_band_visibility(self, band: str, value: str = None):
        """Toggles visibility of a dataset by band

        :param band: Band to toggle (i.e. 'NUV' or 'FUV')
        :param value: Optional parameter to explicitly set the band's visibility to a specific value. 
            Absence will toggle the exising visibility
        """
        # Verify we have data for supplied band
        if self.data_cache.get(band).get('layer'):
            # If the visibility value wasn't explicitly defined, make it the opposite of hte existing visibility value
            # Otherwise, use the supplied value
            if not value: 
                value = not self.data_cache[band]['layer'].visible
            # Set the band's visibility
            self.data_cache[band]['layer'].visible = value

    def mousePressEvent(self, event):
        self._session.application._viewer_in_focus = self
        self._session.application._update_focus_decoration()
        self._session.application._update_plot_dashboard()

class ggui_lightcurve_viewer(ggui_overview_base_viewer, ScatterViewer):
    """Data Viewer class that handles gPhoton lightcurve events"""

    def __init__(self, session: glue.core.session, lightcurve_data: dict, x_att: str = None, y_att: str = None):
        """Initializes an instance of the gPhoton lightcurve viewer

        :param session: Corresponding Glue parent's 'session' object that stores 
        information about the current environment of glue. Needed for superclass constructor
        :param lightcurve_data: Dict containing lightcurve data identified via respective frequency band
        :param x_att: Label of attribute to assign to the x-axis
        :param y_att: Label of attribute to assign to the y-axis
        """
        super().__init__(session, lightcurve_data)
    
        # See DevNote 01: Python Scope
        # Set lightcurve axes to flux vs time
        band_data = list(self.data_cache.values())[0]['data']
        try:
            if x_att:
                self.state.x_att = band_data.id[x_att]
        except KeyError as error:
            print("WARNING: gGui cannot assign lightcurve x axis: " + str(error))
        try:
            if y_att: 
                self.state.y_att = band_data.id[y_att]
        except KeyError as error:
            print("WARNING: gGui cannot assign lightcurve y axis: " + str(error))

        
        # Set default plotting attributes for each dataset
        for datalayer in self.data_cache.values():
            # Set all layers to display a solid line
            datalayer['layer'].linestyle = 'solid'
            datalayer['layer'].line_visible = True
            # Set, and Enable, flux (y axis) error
            datalayer['layer'].yerr_att = datalayer['data'].id['flux_bgsub_err']
            datalayer['layer'].yerr_visible = True


class ggui_image_viewer(ggui_overview_base_viewer, ImageViewer):
    """Data Viewer class that handles gPhoton FITS images"""
    def __init__(self, session: glue.core.session, image_data: dict, x_att: str, y_att: str):
        super().__init__(session, image_data)

@viewer_tool
class fuvToggleTool(Tool):
    """Glue data viewer tool that calls the FUV band visibility toggle method to corresponding ggui data viewer"""
    # Set the boilerplate attributes
    icon = resource_filename('ggui.icons', 'FUV_transparent.png')
    tool_id = 'fuv_toggle'
    tool_tip = 'Toggle the FUV Dataset'

    def __init__(self, viewer):
        """Initializes the toggle tool
        
        :param viewer: The corresponding data viewer this tool belongs to
        """
        super().__init__(viewer)

    def activate(self):
        """Calls the ggui data viewer's data visibility toggle with the 'FUV' band"""
        self.viewer.toggle_band_visibility('FUV')

@viewer_tool
class nuvToggleTool(Tool):
    """Glue data viewer tool that calls the NUV band visibility toggle method to corresponding ggui data viewer"""
    # Set the boilerplate attributes
    icon = resource_filename('ggui.icons', 'NUV_transparent.png')
    tool_id = 'nuv_toggle'
    tool_tip = 'Toggle the NUV Dataset'

    def __init__(self, viewer):
        """Initializes the toggle tool
        
        :param viewer: The corresponding data viewer this tool belongs to
        """
        super().__init__(viewer)

    def activate(self):
        """Calls the ggui data viewer's data visibility toggle with the 'FUV' band"""
        self.viewer.toggle_band_visibility('NUV')

@viewer_tool
class focusTool(Tool):
    """Requests gGui to give the corresponding tool focus"""
    # Set the boilerplate attributes
    icon = resource_filename('ggui.icons', 'Focus.png')
    tool_id = 'focus'
    tool_tip = 'Click to set this viewer to focus'

    def __init__(self, viewer):
        """Initializes the focus tool
        
        :param viewer: The corresponding data viewer this tool belongs to
        """
        super().__init__(viewer)

    def activate(self):
        """Calls the ggui data viewer's data visibility toggle with the 'FUV' band"""
        self.viewer.mousePressEvent(None)

@qt_fixed_layout_tab
class ggui_overview_tab(QtWidgets.QMdiArea):
    """Displays an overview of all gPhoton data products supplied to ggui"""
    
    def __init__(self, session: glue.core.session = None, target_name: str = "Target", target_data: dict = None):
        """Initializes the ggui overview tab with given data

        :param session: Corresponding Glue parent's 'session' object that stores 
        information about the current environment of glue
        :param target_name: The name of the target we are "overviewing"
        :param target_data: The gPhoton data (lighcurves, coadds, cubes) we are "overviewing"
        """
        super().__init__()
        # Set basic tab layout
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
 
        # If we're given any data, go ahead and load it
        if target_data:
            self.load_data(session, target_name, target_data)
       
    def load_data(self, session: glue.core.session, target_name: str, target_data: dict):
        """Constructs the appropriate data viewer for any gPhoton data products provided

        :param session: Corresponding Glue parent's 'session' object that stores 
            information about the current environment of glue.
        :param target_name: The name of the target we are "overviewing"
        :param target_data: The gPhoton data (lighcurves, coadds, cubes) we are "overviewing"
        """
        config = ConfigParser()
        config.read(resource_filename('ggui', 'ggui.conf'))

        # Connect each gPhoton data product to its corresponding load method
        viewer_setters = {
            'lightcurve': self.loadLightcurve,
            'coadd': self.loadCoadd,
            'cube': self.loadCube
        }
        # Clear the board: Remove the existing data viewers
        for widgetIndex in reversed(range(0, self.layout.count())):
            self.layout.removeItem(self.layout.itemAt(widgetIndex))
        # For all the data we've been given, call the appropriate constructor with that data
        for dataType, data in target_data.items():
            try:
                viewer_setters[dataType](session, target_name, data, config.get('Mandatory Fields', dataType + "_x", fallback=None), config.get('Mandatory Fields', dataType + "_y", fallback=None))
            except ValueError as error:
                print("WARNING: " + str(error))
                continue
        
    def loadLightcurve(self, session: glue.core.session, target_name: str, lightcurve_data: dict, x_att: str, y_att: str):
        """Constructs a lightcurve viewer for gPhoton Lightcurve data

        :param session: Corresponding Glue parent's 'session' object that stores 
            information about the current environment of glue.
        :param target_name: The name of the target we are "overviewing"
        :param lightcurve_data: The gPhoton lightcurve to plot
        :param x_att: Label of attribute to assign to the x-axis
        :param y_att: Label of attribute to assign to the y-axis
        """
        # Check for 1-1 correspondence rule (only one data set per band)
        for band, band_data in lightcurve_data.items():
            if isinstance(band_data, list):
                raise ValueError(str(target_name) + " band " + str(band) + " has more than one (" + str(len(band_data)) + ") associated dataset. Cannot plot lightcurve data for this band due to ambiguity.")
        # Construct the data viewer class
        lightCurveViewer = ggui_lightcurve_viewer(session, lightcurve_data, x_att, y_att)
        # Enable the band visibility toggle tools we have data for
        lightCurveViewer.toolbar.actions['fuv_toggle'].setEnabled('FUV' in list(lightcurve_data.keys()))
        lightCurveViewer.toolbar.actions['nuv_toggle'].setEnabled('NUV' in list(lightcurve_data.keys()))
        # Set the title to display the target's name
        lightCurveViewer.axes.set_title("Full Lightcurve of " + target_name)
        lightCurveViewer.axes.set_autoscaley_on(True)
        # Add this viewer to the overview layout
        self.layout.addWidget(lightCurveViewer, 0, 0, 1, 2)
        self.lightCurveViewer = lightCurveViewer
        lightCurveViewer.redraw()

    def loadCoadd(self, session: glue.core.session, target_name: str, coadd_data: dict, x_att: str, y_att: str):
        """Constructs an image viewer for gPhoton Coadd FITS data

        :param session: Corresponding Glue parent's 'session' object that stores 
            information about the current environment of glue.
        :param target_name: The name of the target we are "overviewing"
        :param coadd_data: The gPhoton Coadd to plot
        :param x_att: Label of attribute to assign to the x-axis
        :param y_att: Label of attribute to assign to the y-axis
        """
        # Check for 1-1 correspondence rule (only one data set per band)
        for band, band_data in coadd_data.items():
            if isinstance(band_data, list):
                raise ValueError(str(target_name) + " band " + str(band) + " has more than one (" + str(len(band_data)) + ") associated dataset. Cannot plot coadd data for this band due to ambiguity.")
        # Construct the data viewer class
        coaddViewer = ggui_image_viewer(session, coadd_data, x_att, y_att)
        # Enable the band visibility toggle tools we have data for
        coaddViewer.toolbar.actions['fuv_toggle'].setEnabled('FUV' in list(coadd_data.keys()))
        coaddViewer.toolbar.actions['nuv_toggle'].setEnabled('NUV' in list(coadd_data.keys()))
        # Set the title to display the target's name
        coaddViewer.axes.set_title("CoAdd of " + target_name)
        # Add this viewer to the overview layout
        self.layout.addWidget(coaddViewer, 1, 0)
        self.coaddViewer = coaddViewer

    def loadCube(self, session: glue.core.session, target_name: str , cube_data: dict, x_att: str, y_att: str):
        """Constructs an image viewer for gPhoton Cube FITS data

        :param session: Corresponding Glue parent's 'session' object that stores 
            information about the current environment of glue.
        :param target_name: The name of the target we are "overviewing"
        :param cube_data: The gPhoton Cube to plot
        :param x_att: Label of attribute to assign to the x-axis
        :param y_att: Label of attribute to assign to the y-axis
        """
        # Check for 1-1 correspondence rule (only one data set per band)
        for band, band_data in cube_data.items():
            if isinstance(band_data, list):
                raise ValueError(str(target_name) + " band " + str(band) + " has more than one (" + str(len(band_data)) + ") associated dataset. Cannot plot cube data for this band due to ambiguity.")
        # Construct the data viewer class
        cubeViewer = ggui_image_viewer(session, cube_data, x_att, y_att)
        # Enable the band visibility toggle tools we have data for
        cubeViewer.toolbar.actions['fuv_toggle'].setEnabled('FUV' in list(cube_data.keys()))
        cubeViewer.toolbar.actions['nuv_toggle'].setEnabled('NUV' in list(cube_data.keys()))
        # Set the title to display the target's name
        cubeViewer.axes.set_title("Cube of " + target_name)
        # Add this viewer to the overview layout
        self.layout.addWidget(cubeViewer, 1, 1)
        self.cubeViewer = cubeViewer
