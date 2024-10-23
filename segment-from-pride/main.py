"""

Using AssemblyNet, segment the images from the Philips PRIDE tool 
and prepare the result to be reimported into
the Philips console with PRIDE


----- LICENSE -----
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License (GPL) as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version. For more detail see the
   GNU General Public License at <http://www.gnu.org/licenses/>.
-----------------

Developed by A. Delphin, E. Gourieux, J. Pietras, L. Lamalle
May 2024

"""

import argparse
import json
import os
import sys
from functions import main_processing

from PyQt5.QtCore import QDir
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt5.uic import loadUi


def main_cli():
    """
    Main CLI
    """

    parser = argparse.ArgumentParser(
        description="Obtain information to position MRS voxel "
        "in longitudinal study"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Directory path where 'Sag', 'Cor' and 'Tra' directories are located",
    )

    parser.add_argument(
        "--labels",
        required=True,
        help="Assemblynet labels to use",
        nargs="*",
        default=[181, 185, 201, 207]
    )
    parser.add_argument("--study", required=True, help="Study name")
    parser.add_argument("--patient", required=True, help="Patient name")

    args = parser.parse_args()
    input_dir_path = args.input
    labels = args.labels

    config_file = os.path.join(
            os.path.dirname(os.path.realpath(os.path.dirname(__file__))),
            "config",
            "config.json",
        )

    with open(config_file, encoding="utf-8") as my_json:
        data = json.load(my_json)
        out_directory = data["OutDirectory"]

    if not os.path.exists(out_directory):
        print(
            "Please enter a valid file path in the "
            "configuration file for OutDirectory"
        )
        sys.exit()

    out_directory = os.path.join(
                    out_directory,
                    args.study,
                    args.patient
                )
    if not os.path.exists(out_directory):
        os.makedirs(out_directory)

    # Launch processing
    main_processing(input_dir_path, out_directory, labels)



class App(QMainWindow):
    """
    Main windows Qt
    """

    def __init__(self):
        super(App, self).__init__()
        self.dir_code_path = os.path.realpath(os.path.dirname(__file__))
        # Set window title
        self.setWindowTitle("PRIDE Tool")

        # Set window icon
        icon_path = os.path.join(os.path.dirname(self.dir_code_path), "images", "icon.png")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        # Get ui
        ui_file = os.path.join(self.dir_code_path, "interface.ui")
        loadUi(ui_file, self)

        config_file = os.path.join(
            os.path.dirname(self.dir_code_path),
            "config",
            "config.json",
        )

        with open(config_file, encoding="utf-8") as my_json:
            data = json.load(my_json)
            self.out_directory = data["OutDirectory"]
        if os.path.exists(self.out_directory):
            self.input_directory = self.out_directory
        else:
            self.input_directory = QDir.homePath()

        if not os.path.exists(self.out_directory):
            print(
                "Please enter a valid file path in the "
                "configuration file for OutDirectory"
            )
            sys.exit()
        # Connect signals and slots
        self.pushButton_input.clicked.connect(
            lambda: self.browse_directory("input", self.input_directory)
        )
        self.pushButton_run.clicked.connect(self.get_labels)
        self.pushButton_run.clicked.connect(self.get_patient_name)
        self.pushButton_run.clicked.connect(self.get_study_name)
        self.pushButton_run.clicked.connect(self.launch_processing)

    def get_labels(self):
        """Get Labels from edit line"""
        labels = self.lineEdit_labels.text().split(" ")
        self.labels = [int(i) for i in labels]
        print(self.labels)

    def get_patient_name(self):
        """Get patient name from edit line"""
        self.patient_name = self.lineEdit_patient.text()

    def get_study_name(self):
        """Get study name from edit line"""
        self.study_name = self.lineEdit_study.text()

    def browse_directory(self, name, out):
        """Browse DICOM directory"""
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select a directory",
            os.path.dirname(out),
            options=options,
        )

        if directory:
            if name == "input":
                self.input_dir_path = directory
                self.textEdit_input.setText(self.input_dir_path)

    def launch_processing(self):
        """Launch processing"""
        if self.labels:
            if self.patient_name and self.study_name and self.input_dir_path:
                out_directory = os.path.join(
                    self.out_directory,
                    self.study_name,
                    self.patient_name
                )
                if not os.path.exists(out_directory):
                    os.makedirs(out_directory)

                main_processing(
                    self.input_dir_path,
                    out_directory,
                    self.labels
                )
            else:
                print(
                    "'Study', 'Patient identification' and "
                    "'input directory' fields are mandatory"
                )

        else:
            print("'Labels' field is mandatory")

def main_gui():
    """Main gui"""
    app = QApplication(sys.argv)
    mainwindow = App()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)
    widget.setFixedWidth(800)
    widget.setFixedHeight(600)
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_cli()
    else:
        main_gui()
