from qtpy import QtWidgets
from glue.config import menubar_plugin

import yaml
from glue.core.data_factories import load_data

class targetManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.targetCatalog = {}
        self.primaryTarget = ""
        self.primaryData = {}

    def loadGguiYaml(self, gguiYamlPath):
        self.targetCatalog.update(yaml.load(open(gguiYamlPath, 'r')))

    def loadTargetDict(self, targDict):
        self.targetCatalog.update(targDict)

    def setPrimaryTarget(self, targName):
        if targName is not self.primaryTarget:
            self.primaryTarget = targName
            self.primaryData.clear()
            targetFiles = self.targetCatalog.get(self.primaryTarget)
            for dataProductType in targetFiles:
                self.primaryData[dataProductType] = {}
                for band, bandFile in targetFiles[dataProductType].items():
                    #self.primaryData[dataProductType] = load_data(targetFiles[dataProductType])
                    self.primaryData[dataProductType][band] =load_data(bandFile)
    
    def getPrimaryData(self):
        return self.primaryData

    def getPrimaryName(self):
        return self.primaryTarget

    def getTargetNames(self):
        return self.targetCatalog.keys()


@menubar_plugin("Do something")
def my_plugin(session, data_collection):
    
    return