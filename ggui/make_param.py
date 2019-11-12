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

import pathlib

def validate_target_catalog_file(filepath: str) -> dict:
    """Verifies a gGui Target Catalog confirms to the gGui YAML format

    :returns: verified gGui target dictionary
    """
    return validate_targlist_format(
                yaml.load(open(filepath, "r"), Loader=yaml.BaseLoader),
                filepath
    )

def validate_targlist_format(target_list: dict,  list_source: str) -> dict:
    """Verifies dictionary is in gGui YAML format
    Verifies a given dictionary is the established gGui format.
    Also verifies all specified files exist. Removes any target that does not have any valid files

    :returns: verified gGui target dictionary
    """
    empty_targets = []
    for target_name, target_data in target_list.items():
        valid_files = 0
        for data_type, band_data in target_data.items():
            if data_type == '_notes':
                continue
            for band, filepathString in band_data.items():
                # If a path not specified, or empty string, just skip it
                if filepathString:
                    # If a relative path to the data product is given, join it with respect to the parent Target Catalog path
                    if not pathlib.PurePath(filepathString).is_absolute():
                        # If there are path delimiters, detect which OS it came from to interpret the path directly
                        if "\\" in filepathString:
                            filepathString = str(pathlib.PurePath(list_source).parent.joinpath(pathlib.PureWindowsPath(filepathString)))
                        elif "/" in filepathString:
                            filepathString = str(pathlib.PurePath(list_source).parent.joinpath(pathlib.PurePosixPath(filepathString)))
                        else:
                            filepathString = str(pathlib.PurePath(list_source).parent.joinpath(pathlib.PurePath(filepathString)))
                    if not pathlib.Path(filepathString).is_file():
                        print("Cannot find " + filepathString + " on disk. Ignoring...")
                    else: valid_files += 1
        if not valid_files:
            empty_targets.append(target_name)

    for bad_target in empty_targets:
        print(str(bad_target) + " does not have any valid data. Ignoring target...")
        del target_list[bad_target]

    return target_list

def quoted_presenter(dumper, data):
    """
    This is a custom representer for string, so that YAML can be output
    with quotes to satisfy paths on Windows.
    """
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

class MakeParamGUI(QtWidgets.QWidget):
    """
    This class builds a pyQt GUI for creating a GGUI YAML parameter file.
    """

    def __init__(self):
        yaml.add_representer(str, quoted_presenter)
        super().__init__()
        self.input_fname = ''
        self.output_fname = ''
        self.output_save_text = ''
        self.input_save_text = ''
        self.log_display = ''
        self.load_button = QPushButton()
        self.save_button = QPushButton()
        self.iscrollarea = QScrollArea()
        self.yaml_params = dict()
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
                input_fname_root = os.path.join(
                    os.path.dirname(self.input_fname), '')
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
                            prikey = row[0].strip()
                            self.yaml_params[prikey] = {'lightcurve':{},
                                                        'coadd':{}, 'cube':{}}
                            if row[1].strip():
                                self.yaml_params[prikey]['lightcurve']['FUV'] = (
                                    os.path.abspath(input_fname_root +
                                                    row[1].strip()))
                            if row[2].strip():
                                self.yaml_params[prikey]['lightcurve']['NUV'] = (
                                    os.path.abspath(input_fname_root +
                                                    row[2].strip()))
                            if row[3].strip():
                                self.yaml_params[prikey]['coadd']['FUV'] = (
                                    os.path.abspath(input_fname_root +
                                                    row[3].strip()))
                            if row[4].strip():
                                self.yaml_params[prikey]['coadd']['NUV'] = (
                                    os.path.abspath(input_fname_root +
                                                    row[4].strip()))
                            if row[5].strip():
                                self.yaml_params[prikey]['cube']['FUV'] = (
                                    os.path.abspath(input_fname_root +
                                                    row[5].strip()))
                            if row[6].strip():
                                self.yaml_params[prikey]['cube']['NUV'] = (
                                    os.path.abspath(input_fname_root +
                                                    row[6].strip()))
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
            yaml.dump(self.yaml_params, outfile, default_flow_style=False)

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
