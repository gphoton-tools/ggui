from qtpy import QtWidgets
from glue.config import menubar_plugin

import yaml
from glue.core.data_factories import load_data

class targetManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.targetCatalog = {}
        self.primaryTarget = None

    def loadGguiYaml(self, gguiYamlPath):
        self.targetCatalog.update(yaml.load(open(gguiYamlPath, 'r')))

    def loadTargetDict(self, targDict):
        self.targetCatalog.update(targDict)

    def setPrimaryTarget(self, targName):
        self.primaryTarget = targName
    
    def getPrimaryData(self):
        targetFiles = self.targetCatalog.get(self.primaryTarget)
        dataDict = {}
        for dataProductType in targetFiles:
            dataDict[dataProductType] = load_data(targetFiles[dataProductType])
        return dataDict
    

    
    def getTarget(self, targName):
        return self.targetCatalog.get(targName, {})

    def getTargetNames(self):
        return self.targetCatalog.keys()


@menubar_plugin("Do something")
def my_plugin(session, data_collection):
    
    return