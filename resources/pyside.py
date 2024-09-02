from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt, QThread, Signal
import sys
import traceback
import logging

# Import Main Engine Class to run the process thread
from lib.main_engine import MainEngine
from lib.utils import Utils

class WorkerThread(QThread):
    finished = Signal(str)

    def run(self):
        try:
            main_client = MainEngine()
            main_client.cli()
            self.finished.emit("Slicing completed successfully.")
        except Exception as e:
            logging.basicConfig(filename=Utils.get_resource_path('error_log.txt'), level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
            logging.error("An error occurred: %s", str(e), exc_info=True)
            error_message = "An error occurred. Please check the error_log.txt file for more details."
            self.finished.emit(error_message)
            traceback.print_exc()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Sandwiched Slicer Tool")
        self.setGeometry(300, 300, 600, 400)

        # Create the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout
        layout = QVBoxLayout(central_widget)

        # Create a text area to display initial information
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(
            "(C) 19/07/2024\n"
            "Edited 21/08/2024\n"
            "University of Leeds, 2024\n"
            "School of Mechanical Engineering\n\n"
            "Custom Sandwiched Slicer Tool for slicing and generating toolpaths for the AMPI\n"
            "machine with custom tools.\n\n"
            "Written and Designed by Pralish Satyal\n"
            "el19ps@leeds.ac.uk\n"
            "P.Satyal@leeds.ac.uk\n\n"
            "pralishbusiness@gmail.com"
        )
        layout.addWidget(self.text_area)

        # Create a button to start the slicing process
        self.start_button = QPushButton("Start Slicing")
        self.start_button.clicked.connect(self.start_slicing)
        layout.addWidget(self.start_button)

        # Create a label to show the status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def start_slicing(self):
        self.status_label.setText("Slicing in progress...")
        self.start_button.setDisabled(True)

        self.worker_thread = WorkerThread()
        self.worker_thread.finished.connect(self.on_slicing_finished)
        self.worker_thread.start()

    def on_slicing_finished(self, message):
        self.status_label.setText(message)
        self.start_button.setDisabled(False)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
