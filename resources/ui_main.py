import sys
from PyQt5.QtWidgets import QApplication
from lib.ui_engine import SupremeSlicerUI

# Run the application
def main():
    # Create an instance of the QApplication
    app = QApplication(sys.argv)

    # Create the main window from SupremeSlicerUI (PyQt5 window)
    main_window = SupremeSlicerUI()

    # Show the main window
    main_window.show()

    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
