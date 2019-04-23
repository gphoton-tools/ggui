"""
.. module:: make_param.py
    :synopsis: GUI used to create input param files needed to run GGUI.
.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""
import csv
import os
import sys
import yaml
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
        self.input_fname = ''
        self.output_fname = ''
        self.output_save_text = ''
        self.input_save_text = ''
        self.log_display = ''
        self.load_button = QPushButton()
        self.save_button = QPushButton()
        self.iscrollarea = QScrollArea()
        self.yaml_params = []
        self.init_ui()

    def getifile(self):
        """
        Retrieves selected file names and populates text box area with it.
        """
        self.input_fname, _filter = QFileDialog.getOpenFileName(
            self, 'Select Input File')
        self.input_save_text.setPlaceholderText(self.input_fname)

    def update_ofile(self):
        """
        Updates the output file name if text is entered or changed in the box.
        """
        self.output_fname = self.output_save_text.text().strip()
        # If the input_fname is set, then activate the save button.
        if self.input_fname:
            self.save_button.setStyleSheet(
                "QPushButton { background-color:"
                '"#7af442";border-color:"#45a018";}')
            self.save_button.setEnabled(True)
        # If the user has deleted all the text, disable the button.
        if not self.output_fname:
            self.save_button.setStyleSheet("QPushButton { background-color:"
                                           '"#FF4242";border-color:"#45a018";}')
            self.save_button.setEnabled(False)

    def make_output_row(self):
        """
        Create the row containing the output control.
        """
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
        self.output_save_text.textChanged.connect(self.update_ofile)
        self.grid.addWidget(self.output_save_text, 0, 1, 1, 1)
        # This is the Save button for the output file.
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet("QPushButton { background-color:"
                                       '"#FF4242";border-color:"#45a018";}')
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_yaml)
        self.grid.addWidget(self.save_button, 0, 2, 1, 1)

    def load_file(self):
        """
        Actions performed when pressing the Load button.
        Any row that begins with a pound sign charater is skipped.
        """
        if self.input_fname:
            with open(self.input_fname, 'r') as input_file:
                csv_reader = csv.reader(input_file, delimiter=',')
                row_num = 0
                for row in csv_reader:
                    row_num = row_num + 1
                    if row[0].lstrip()[0] != '#':
                        if len(row) == 7:
                            # Then found expected number of entries.  Add this
                            # target to the list object to prepare for yaml
                            # output.
                            testfs = row[1:]
                            
                            # Check for file existence.
                            for testf in testfs:
                                if not os.path.isfile(testf) and testf:
                                    self.log_display.append("File not found: "
                                                            + testf)

                            self.yaml_params.append({row[0].strip():{
                                'lightcurve':{'FUV':row[1].strip(),
                                              'NUV':row[2].strip()},
                                'coadd':{'FUV':row[3].strip(),
                                         'NUV':row[4].strip()},
                                'cube':{'FUV':row[5].strip(),
                                        'NUV':row[6].strip()}}})
                        else:
                            # Then need to print an error to the log area.
                            err_string = ("Row number {0:d}".format(row_num) +
                                          " does not have seven columns.")
                            self.log_display.append(err_string)
                # After parsing the CSV, enable the Save button.
                # Only enable if an output file has been decided.
                if self.output_fname:
                    self.save_button.setStyleSheet(
                        "QPushButton { background-color:"
                        '"#7af442";border-color:"#45a018";}')
                    self.save_button.setEnabled(True)

    def save_yaml(self):
        """
        Writes yaml parameters to file.
        """
        with open(self.output_fname, 'w') as outfile:
            yaml.dump(self.yaml_params, outfile)

    def make_input_row(self):
        """
        Create the row containing the input control.
        """
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
        self.load_button.clicked.connect(self.load_file)
        self.grid.addWidget(self.load_button, 1, 2, 1, 1)

    def make_errorlog_row(self):
        """
        Create the row containing the error log area.
        """
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
    APP = QApplication(sys.argv)
    W = MakeParamGUI()
    sys.exit(APP.exec_())
