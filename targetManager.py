from qtpy import QtWidgets
from glue.config import menubar_plugin
from glue.core.link_helpers import LinkSame

import yaml
from glue.core.data_factories import load_data

class targetManager(QtWidgets.QWidget):
    def __init__(self, glueParent):
        super().__init__()
        self.glueParent = glueParent

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
                    self.primaryData[dataProductType][band] = load_data(bandFile)

                bands = self.primaryData[dataProductType].keys()
                if len(bands) > 1:
                    attributesToGlue = {'lightcurve': ['t_mean', 'flux_bgsub'], 'coadd': ['Right Ascension', 'Declination'], 'cube': ['Right Ascension', 'Declination']}
                    for glueAttribute in attributesToGlue[dataProductType]:
                        #dataCollection.add_link(LinkSame(somehow add all bands here stored in the bands key above))
                        #Can only link two fields at a time. Need to go through all combinations
                        import itertools
                        for linkingPair in (set(frozenset(t) for t in itertools.permutations(self.primaryData['lightcurve'].values(),2))):
                        #for linkingPair in (set(tuple(sorted(t)) for t in itertools.permutations(self.primaryData['lightcurve'].values(),2))):
                            accessor = tuple(linkingPair)
                            self.glueParent.data_collection.add_link(LinkSame(accessor[0].id[glueAttribute],accessor[1].id[glueAttribute]))
                            #self.glueParent.data_collection.add_link(LinkSame(linkingPair[0].id[glueAttribute]))

    
    def getPrimaryData(self):
        return self.primaryData

    def getPrimaryName(self):
        return self.primaryTarget

    def getTargetNames(self):
        return self.targetCatalog.keys()


@menubar_plugin("Do something")
def my_plugin(session, data_collection):
    
    return