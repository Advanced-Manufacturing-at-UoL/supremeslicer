"""
(C) 16/09/2024
Editted 16/09/2024
University of Leeds, 2024
School of Mechanical Engineering

Custom Slicer Tool for slicing and generating toolpaths for the AMPI
machine with custom tools. Current verion is V1.3.X. This code has a
toolpath renderer as well as a animation tool for rendering the toolpath.

THIS VERSION CREATES A BASIC UI

Fully Written and Designed by Pralish Satyal
el19ps@leeds.ac.uk
P.Satyal@leeds.ac.uk
pralishbusiness@gmail.com
"""
import sys
from PyQt5.QtWidgets import QApplication
from lib.ui_engine import SupremeSlicerUI

# Run the application
def main():
    app = QApplication(sys.argv)

    main_window = SupremeSlicerUI()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
