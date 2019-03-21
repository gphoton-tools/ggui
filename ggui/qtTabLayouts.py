import sys
import pathlib
from PyQt5 import QtWidgets
from glue.config import qt_fixed_layout_tab, viewer_tool
from glue.viewers.common.qt.tool import Tool

from glue.viewers.matplotlib.qt.data_viewer import MatplotlibDataViewer
from glue.viewers.scatter.qt import ScatterViewer
from glue.viewers.image.qt import ImageViewer

class gguiOverviewBaseViewer(MatplotlibDataViewer):
    
    tools = ['fuv_toggle', 'nuv_toggle']
    
    def __init__(self, session, data):
        super().__init__(session)
        self.dataLib = {}
        for band, bandData in data.items():
            self.add_data(bandData)
            # Horrible performance. Go back and fix!
            for index, layerData in enumerate([layers.layer for layers in self.state.layers]):
                if layerData == bandData:
                    self.dataLib[band] = {'data': bandData, 'layer': self.state.layers[index]}
                    break
        # Associate FUV datasets with the color blue, and NUV datasets with the color red
        if 'FUV' in self.dataLib:
            self.dataLib['FUV']['layer'].color = 'blue'
        if 'NUV' in self.dataLib:
            self.dataLib['NUV']['layer'].color = 'red'
        
    def toggleBandScatter(self, band, value=None):
        if self.dataLib.get(band).get('layer'):
            if value is None: value = not self.dataLib[band]['layer'].visible
            #self.dataLib[band]['layer'].visible = not self.dataLib[band]['layer'].visible
            self.dataLib[band]['layer'].visible = value

    def mousePressEvent(self, event):
        self._session.application._viewer_in_focus = self
        self._session.application._update_focus_decoration()
        self._session.application._update_plot_dashboard()


class gguiLightcurveViewer(gguiOverviewBaseViewer, ScatterViewer):

    def __init__(self, session, lightCurveData):
        super().__init__(session, lightCurveData)
    
        # See DevNote 01: Python Scope
        # Set lightcurve axes to flux vs time
        bandData = list(self.dataLib.values())[0]['data']
        self.state.x_att = bandData.id['t_mean']
        self.state.y_att = bandData.id['flux_bgsub']
        

        for datalayer in self.dataLib.values():
            # Set all layers to display a solid line
            datalayer['layer'].linestyle = 'solid'
            datalayer['layer'].line_visible = True
            # Set, and Enable, flux (y axis) error
            datalayer['layer'].yerr_att = datalayer['data'].id['flux_bgsub_err']
            datalayer['layer'].yerr_visible = True


class duyImageViewer(gguiOverviewBaseViewer, ImageViewer):
    pass

@viewer_tool
class fuvToggleTool(Tool):
    icon = str(pathlib.Path.cwd() / 'icons' / 'FUV_transparent.png')
    tool_id = 'fuv_toggle'
    tool_tip = 'Toggle the FUV Dataset'

    def __init__(self, viewer):
        super().__init__(viewer)

    def activate(self):
        self.viewer.toggleBandScatter('FUV')

@viewer_tool
class nuvToggleTool(Tool):
    icon = str(pathlib.Path.cwd() / 'icons' / 'NUV_transparent.png')
    tool_id = 'nuv_toggle'
    tool_tip = 'Toggle the NUV Dataset'

    def __init__(self, viewer):
        super().__init__(viewer)

    def activate(self):
        self.viewer.toggleBandScatter('NUV')

@qt_fixed_layout_tab
class overviewTabLayout(QtWidgets.QMdiArea):
    
    def __init__(self, parent=None, session=None, targName="Target", targData={}):
        super().__init__()

        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
 
        if targName and targData:
            self.load_data(session, targName, targData)
       
    def load_data(self, session, target_name, target_data):
        viewer_setters = {'lightcurve': self.loadLightcurve, 'coadd': self.loadCoadd, 'cube': self.loadCube}
        for dataType, data in target_data.items():
            viewer_setters[dataType](session, data, target_name)
    
    def loadLightcurve(self, session, lightCurveData, targName):
        lightCurveViewer = gguiLightcurveViewer(session, lightCurveData)

        lightCurveViewer.toolbar.actions['fuv_toggle'].setEnabled('FUV' in list(lightCurveData.keys()))
        lightCurveViewer.toolbar.actions['nuv_toggle'].setEnabled('NUV' in list(lightCurveData.keys()))
        
        lightCurveViewer.axes.set_title("Full Lightcurve of " + targName)
        
        self.layout.addWidget(lightCurveViewer, 0, 0, 1, 2)
        self.lightCurveViewer = lightCurveViewer

    def loadCoadd(self, session, coaddData, targName):
        coaddViewer = duyImageViewer(session, coaddData)

        coaddViewer.toolbar.actions['fuv_toggle'].setEnabled('FUV' in list(coaddData.keys()))
        coaddViewer.toolbar.actions['nuv_toggle'].setEnabled('NUV' in list(coaddData.keys()))

        coaddViewer.axes.set_title("CoAdd of " + targName)

        self.layout.addWidget(coaddViewer, 1, 0)
        self.coaddViewer = coaddViewer

    def loadCube(self, session, cubeData, targName):
        cubeViewer = duyImageViewer(session, cubeData)

        cubeViewer.toolbar.actions['fuv_toggle'].setEnabled('FUV' in list(cubeData.keys()))
        cubeViewer.toolbar.actions['nuv_toggle'].setEnabled('NUV' in list(cubeData.keys()))
        
        cubeViewer.axes.set_title("Cube of " + targName)
        
        self.layout.addWidget(cubeViewer, 1, 1)
        self.cubeViewer = cubeViewer
