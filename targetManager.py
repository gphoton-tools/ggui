from qtpy import QtWidgets
from glue.config import menubar_plugin

class targetManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.targetCatalog = {}

    def loadTargets(self, targDict):
        self.targetCatalog.update(targDict)]
    
    def getTarget(self, targName):
        return self.targetCatalog.get(targName, {})

    def getTargetNames(self):
        return self.targetCatalog.keys()


@menubar_plugin("Do something")
def my_plugin(session, data_collection):
    
    return