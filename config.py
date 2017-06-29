
from glue.config import settings, preference_panes
from qtpy import QtWidgets


class GGUIPreferences(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super(GGUIPreferences, self).__init__(parent=parent)

        self.layout = QtWidgets.QFormLayout()

        self.option1 = QtWidgets.QCheckBox()
        self.option2 = QtWidgets.QCheckBox()
        self.option3 = QtWidgets.QCheckBox()

        self.layout.addRow("Prompt for Lightcurves", self.option1)
        self.layout.addRow("Prompt for CoAdds", self.option2)
        self.layout.addRow("Prompt for Cubes", self.option3)

        self.setLayout(self.layout)

        self.option1.setChecked(settings.OPTION1)
        self.option2.setChecked(settings.OPTION2)
        self.option3.setChecked(settings.OPTION3)

    def finalize(self):
        settings.OPTION1 = self.option1.isChecked()
        settings.OPTION2 = self.option2.isChecked()
        settings.OPTION3 = self.option3.isChecked()


settings.add('OPTION1', False, bool)
settings.add('OPTION2', False, bool)
settings.add('OPTION3', False, bool)
preference_panes.add('GGUI Preferences', GGUIPreferences)