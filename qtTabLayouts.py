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
                    self.dataLib[band] = {'Data': bandData, 'layer': self.state.layers[index]}
                    break
        
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
        bandData = list(self.dataLib.values())[0]['Data']
        self.state.x_att = bandData.id['t_mean']
        self.state.y_att = bandData.id['flux_bgsub']
        

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


'''
#@qt_fixed_layout_tab
class overviewTabLayout(QtWidgets.QWidget):
    def __init__(self, parent=None, session=None):
        super(overviewTabLayout, self).__init__(parent)
        #print("Parent: " + str(parent))
        #print("Session: " + str(session.application))

        glueApp = session.application
        print(str(glueApp.viewers))

        #lightcurveViewer = glueApp.choose_new_data_viewer()
        #coAddViewer = glueApp.choose_new_data_viewer()
        #cubeViewer = glueApp.choose_new_data_viewer()
        lightcurveViewer, coAddViewer, cubeViewer = glueApp.viewers[0]
        
        self.setGeometry(100,100,200,50)
        #button1 = QtWidgets.QPushButton("One", self)
        #button1.move(0,0)
        #button2 = QtWidgets.QPushButton("Two", self)
        #button2.move(10,10)
        #button3 = QtWidgets.QPushButton("Three", self)
        #button3.move(20,20)
        #button4 = QtWidget.QPushButton("Four")
        #button5 = QtWidget.QPushButton("Five")

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        #loadWidgets(lightcurveViewer, coAddViewer, cubeViewer)
        layout.addWidget(lightcurveViewer, 0, 0, 1, 2)
        layout.addWidget(cubeViewer, 1, 1)
        layout.addWidget(coAddViewer, 1, 0)
        #self.activeSubWindow = lightcurveViewer
        print("\n\nErrors Below:\n---------------------------------")
    
#@qt_fixed_layout_tab
class testLayout(QtWidgets.QWidget):
    def __init__(self, parent=None, session=None):
        super(testLayout, self).__init__(parent)
        self.setGeometry(100,100,200,50)
        button1 = QtWidgets.QPushButton("One", self)
        button2 = QtWidgets.QPushButton("Two", self)
        button3 = QtWidgets.QPushButton("Three", self)

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        layout.addWidget(button3, 0, 0, 1, 2)
        layout.addWidget(button1, 1, 1)
        layout.addWidget(button2, 1, 0)

        self.subWindowActivated = button1

    def activeSubWindow(self):
        print("Hello World!")
'''
'''
myQApp = QtWidgets.QApplication(sys.argv)
myWidget = testLayout()

myWidget.setGeometry(100,100,200,50)
myWidget.setWindowTitle("PyQt")
myWidget.show()
sys.exit(myQApp.exec_())
-----
myQApp = QtWidgets.QApplication(sys.argv)

mainWidget = overviewTabLayout()

button1 = QtWidgets.QPushButton("One")
button2 = QtWidgets.QPushButton("Two")
button3 = QtWidgets.QPushButton("Three")

mainWidget.loadWidgets(lightcurveViewer=button1, coAddViewer=button2, cubeViewer=button3)

mainWidget.setWindowTitle("Glue Test")
mainWidget.show()
sys.exit(myQApp.exec_())
'''