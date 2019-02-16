from collections import OrderedDict

from qtpy import QtWidgets
from glue.config import menubar_plugin
from glue.core.link_helpers import LinkSame
from glue.core.data_factories import load_data

class target_manager(QtWidgets.QWidget):
    def __init__(self, glueParent):
        super().__init__()
        self.glueParent = glueParent

        self.targetCatalog = OrderedDict()
        self.primaryName = ""
        self.primaryData = {}

    def loadTargetDict(self, targDict):
        self.targetCatalog.update(targDict)

    def setPrimaryTarget(self, targName):
        if targName is not self.primaryName:
            self.primaryName = targName
            self.primaryData.clear()
            targetFiles = self.targetCatalog.get(self.primaryName)
            # For each gGui Data Type...
            for dataProductType in targetFiles:
                self.primaryData[dataProductType] = {}
                # Load every band's data
                for band, bandFile in targetFiles[dataProductType].items():
                    self.primaryData[dataProductType][band] = load_data(bandFile)
                # If we have multiple bands, glue them together
                bands = self.primaryData[dataProductType].keys()
                if len(bands) > 1:
                    attributesToGlue = {'lightcurve': ['t_mean', 'flux_bgsub'], 
                                        'coadd': ['Right Ascension', 'Declination'], 
                                        'cube': ['Right Ascension', 'Declination', 'World 0']}
                    for glueAttribute in attributesToGlue[dataProductType]:
                        #dataCollection.add_link(LinkSame(somehow add all bands here stored in the bands key above))
                        #Can only link two fields at a time. Need to go through all combinations
                        import itertools
                        for linkingPair in (set(frozenset(t) for t in itertools.permutations(self.primaryData[dataProductType].values(),2))):
                        #for linkingPair in (set(tuple(sorted(t)) for t in itertools.permutations(self.primaryData['lightcurve'].values(),2))):
                            accessor = tuple(linkingPair)
                            self.glueParent.data_collection.add_link(LinkSame(accessor[0].id[glueAttribute],accessor[1].id[glueAttribute]))
                            #self.glueParent.data_collection.add_link(LinkSame(linkingPair[0].id[glueAttribute]))

    def getPrimaryData(self):
        return self.primaryData

    def getPrimaryName(self):
        return self.primaryName

    def getTargetNames(self):
        return self.targetCatalog.keys()

    def next_target(self):
        current_target_index = list(self.targetCatalog.keys()).index(self.primaryName)
        next_target_index = current_target_index + 1
        if next_target_index > int(len(self.targetCatalog.keys())) - 1:
            next_target_index = 0
        next_target_name = list(self.targetCatalog.keys())[next_target_index]
        self.setPrimaryTarget(next_target_name)

    
@menubar_plugin("Next Target")
def next_target_plugin(session, data_collection):
    # Remove the existing primary target's datasets
    for band_data_set in list(session.application.target_manager.getPrimaryData().values()):
        for band_data in band_data_set.values():
            session.application.data_collection.remove(band_data)
    # Advance target manager to the next target
    session.application.next_target()
    # Regenerate the overview tab with the new data
    session.application.overview_tab.load_data(session, 
                                               session.application.target_manager.getPrimaryName(), 
                                               session.application.target_manager.getPrimaryData())

