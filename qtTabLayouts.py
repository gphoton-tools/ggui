import sys
from qtpy import QtWidgets
from glue.config import qt_fixed_layout_tab

from glue.viewers.scatter.qt import ScatterViewer
from glue.viewers.image.qt import ImageViewer
class duyScatterViewer(ScatterViewer):
    def mousePressEvent(self, event):
        self._session.application._viewer_in_focus = self
        self._session.application._update_focus_decoration()
        self._session.application._update_plot_dashboard()

class duyImageViewer(ImageViewer):
    def mousePressEvent(self, event):
        self._session.application._viewer_in_focus = self
        self._session.application._update_focus_decoration()
        self._session.application._update_plot_dashboard()

glueDataProductClasses = {'lightcurve': duyScatterViewer, 'coadd': duyImageViewer, 'cube': duyImageViewer}

@qt_fixed_layout_tab
class overviewTabLayout(QtWidgets.QMdiArea):
    
    

    def __init__(self, parent=None, session=None, targData={}):
        super().__init__()
        viewerSetters = {'lightcurve': self.loadLightcurve, 'coadd': self.loadCoadd, 'cube': self.loadCube}


        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
 
        glueApp = session.application
        #lightcurveViewer, coAddViewer, cubeViewer = glueApp.viewers[0]

        for dataType, data in targData.items():
            glueApp.data_collection.append(data)
            viewer = glueDataProductClasses[dataType](session)
            viewer.add_data(data)
            viewerSetters[dataType](viewer)
       
    def loadLightcurve(self, lightCurveViewer):
        self.layout.addWidget(lightCurveViewer, 0, 0, 1, 2)

    def loadCoadd(self, coAddViewer):
        self.layout.addWidget(coAddViewer, 1, 0)

    def loadCube(self, cubeViewer):
        self.layout.addWidget(cubeViewer, 1, 1)


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