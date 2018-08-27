from glue.config import settings, preference_panes
from qtpy import QtWidgets

from glue.config import viewer_tool
from glue.viewers.common.qt.tool import Tool

@viewer_tool
class GGUIAutoChop(Tool):

    icon = 'myicon.png'
    tool_id = 'custom_tool'
    action_text = 'Does cool stuff'
    tool_tip = 'Does cool stuff'
    shortcut = 'D'

    def __init__(self, viewer):
        super(MyCustomMode, self).__init__(viewer)

    def activate(self):
        pass

    def close(self):
        pass


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


settings.add('OPTION1', True, bool)
settings.add('OPTION2', True, bool)
settings.add('OPTION3', True, bool)
preference_panes.add('GGUI Preferences', GGUIPreferences)