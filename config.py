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
