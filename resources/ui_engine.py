import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, 
                             QMessageBox, QTextEdit, QVBoxLayout, QWidget, QToolBar)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from lib.utils import Utils
from lib.main_engine import MainEngine


class SupremeSlicerUI(QMainWindow):
    """Main GUI Window for SupremeSlicer using PyQt5"""

    def __init__(self):
        super().__init__()
        self.initUI()
        self.main_engine = MainEngine()

    def initUI(self):
        """Initialize the main window UI components."""
        self.setWindowTitle("SupremeSlicer GUI")
        self.setGeometry(100, 100, 800, 600)

        # Create a central text display area
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.setCentralWidget(self.text_display)

        # Set up the Menu Bar
        self.createMenuBar()

        # Set up the Toolbar
        self.createToolBar()

    def createMenuBar(self):
        """Create the main menu bar with various options."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        open_config_action = QAction('Open Config', self)
        open_config_action.setShortcut('Ctrl+O')
        open_config_action.triggered.connect(self.read_config)
        file_menu.addAction(open_config_action)

        exit_action = QAction(QIcon('exit.png'), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu('Tools')

        vacuum_action = QAction('VacuumPnP Tool', self)
        vacuum_action.triggered.connect(self.run_vacuum_tool)
        tools_menu.addAction(vacuum_action)

        simulation_action = QAction('Run Simulation', self)
        simulation_action.triggered.connect(self.run_simulation)
        tools_menu.addAction(simulation_action)

        animation_action = QAction('Render Animation', self)
        animation_action.triggered.connect(self.run_animation)
        tools_menu.addAction(animation_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        documentation_action = QAction('Show Documentation', self)
        documentation_action.triggered.connect(self.show_documentation)
        help_menu.addAction(documentation_action)

    from PyQt5.QtCore import Qt

    def createToolBar(self):
        """Create the main toolbar with quick access buttons."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Set the style of the toolbar buttons to show the text under the icon
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Add toolbar actions with icons and text labels
        slice_action = QAction(QIcon('slice.png'), 'Slice G-code', self)
        slice_action.setToolTip("Slice an STL file into G-code")  # Add tooltip for description
        slice_action.triggered.connect(self.run_slicer)
        toolbar.addAction(slice_action)

        viewer_action = QAction(QIcon('stl.png'), 'Run STL Viewer', self)
        viewer_action.setToolTip("View the STL file")
        viewer_action.triggered.connect(self.run_stl_viewer)
        toolbar.addAction(viewer_action)

        part_info_action = QAction(QIcon('info.png'), 'Part Info', self)
        part_info_action.setToolTip("Get information about the part")
        part_info_action.triggered.connect(self.get_part_info)
        toolbar.addAction(part_info_action)

    def display_message(self, message):
        """Display messages in the central text area."""
        self.text_display.append(message + '\n')

    # The following methods correspond to menu and toolbar actions
    def read_config(self):
        """Open and display the config file."""
        try:
            config_data = Utils.read_yaml(Utils.get_resource_path(r'configs/config.yaml'))
            config_info = "\n".join([f"{k}: {v}" for k, v in config_data.items()])
            self.display_message("Config File:\n" + config_info)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading config file: {str(e)}")

    def run_slicer(self):
        """Run the slicer and display the result."""
        try:
            self.main_engine._run_slicer()
            self.display_message("G-code slicing completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running slicer: {str(e)}")

    def run_stl_viewer(self):
        """Run the STL viewer."""
        try:
            self.main_engine._run_stl_viewer()
            self.display_message("STL viewer started.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running STL viewer: {str(e)}")

    def get_part_info(self):
        """Obtain and display part information."""
        try:
            self.main_engine._get_part_info()
            self.display_message("Part information displayed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error getting part info: {str(e)}")

    def run_vacuum_tool(self):
        """Run the VacuumPnP tool."""
        try:
            self.main_engine._vacuum_tool()
            self.display_message("VacuumPnP tool completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running VacuumPnP tool: {str(e)}")

    def run_simulation(self):
        """Run the simulation."""
        try:
            self.main_engine._run_simulation()
            self.display_message("Simulation completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running simulation: {str(e)}")

    def run_animation(self):
        """Run the animation tool."""
        try:
            self.main_engine._run_animation()
            self.display_message("Animation rendering completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running animation: {str(e)}")

    def show_documentation(self):
        """Display the documentation."""
        doc_text = (
            "This tool was made by Pralish Satyal and can slice an STL, converting it to GCODE.\n"
            "It allows custom G-Code injection for custom tools such as the VacuumPnP.\n"
            "Custom tools include the general extruder, the VacuumPnP tool, the screwdriver, and the gripper."
        )
        QMessageBox.information(self, "Documentation", doc_text)



