"""
.. module:: make_param.py
    :synopsis: GUI used to create input param files needed to run GGUI.
.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""
import yaml
import sys
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    import PyQt5.QtWidgets as QtWidgets
    from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QFileDialog
    from PyQt5.QtWidgets import QTextEdit, QScrollArea
except ImportError:
    from PyQt4.QtCore import Qt
    from PyQt4.QtGui import QFont
    import PyQt4.QtWidgets as QtWidgets
    from PyQt4.QtWidgets import QApplication, QLineEdit, QPushButton, QFileDialog
    from PyQt4.QtWidgets import QTextEdit, QScrollArea

class MakeParamGUI(QtWidgets.QWidget):
    """
    This class builds a pyQt GUI for creating a GGUI YAML parameter file.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def getifile(self):
        self.input_fname, _filter = QFileDialog.getOpenFileName(
            self,'Select Input File')
        self.input_save_text.setPlaceholderText(self.input_fname)

    def make_output_row(self):
        # This creates the label itself.
        output_save_label = QtWidgets.QLabel('Output File Name: ')
        output_save_label.setAlignment(Qt.AlignLeft)
        output_save_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.grid.addWidget(output_save_label, 0, 0, 1, 1)
        # This creates the current save file text area.
        self.output_save_text = QLineEdit()
        self.output_save_text.setReadOnly(False)
        self.output_save_text.setStyleSheet("border-style: solid; "
                                            "border-width: 1px; "
                                            "background: white; ")
        self.grid.addWidget(self.output_save_text, 0, 1, 1, 1)
        # This is the Save button for the output file.
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet("QPushButton { background-color:"
                                       '"#7af442";border-color:"#45a018";}')
        self.grid.addWidget(self.save_button, 0, 2, 1, 1)

    def make_input_row(self):
        # This creates the label itself.
        input_save_label = QtWidgets.QLabel('Input File Name: ')
        input_save_label.setAlignment(Qt.AlignLeft)
        input_save_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.grid.addWidget(input_save_label, 1, 0, 1, 1)
        # This creates the current input file name that was loaded.
        self.input_save_text = QLineEdit()
        self.input_save_text.setReadOnly(True)
        self.input_save_text.setStyleSheet("border-style: solid; "
                                            "border-width: 1px; "
                                            "background: white; ")
        self.iscrollarea = QScrollArea(self)
        self.iscrollarea.setWidget(self.input_save_text)
        self.iscrollarea.setWidgetResizable(True)
        self.grid.addWidget(self.iscrollarea, 1, 1, 1, 1)
        # This creates the file picker button to select the input file.
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.getifile)
        self.load_button.setStyleSheet("QPushButton { background-color:"
                                       '"#7af442";border-color:"#45a018";}')
        self.grid.addWidget(self.load_button, 1, 2, 1, 1)

    def make_errorlog_row(self):
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.NoWrap)
        self.log_display.setStyleSheet("border-style: solid; "
                                            "border-width: 1px; "
                                            "background: white; ")
        self.grid.addWidget(self.log_display, 2, 0, 1, 3)

    def init_ui(self):
        """
        Defines the GUI layout, text fields, buttons, etc.
        """
        # Create a grid layout and add all the widgets.
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

        # Create the row that contains the parameter file save options.
        self.make_output_row()

        # Create the row that contains the input upload controls.
        self.make_input_row()

        # Create the row that contains the error log area.
        self.make_errorlog_row()
        
        # Display the GUI.
        self.setLayout(self.grid)
        self.resize(800, 300)
        self.setWindowTitle("Create GGUI Input File")
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MakeParamGUI()
    sys.exit(app.exec_())

