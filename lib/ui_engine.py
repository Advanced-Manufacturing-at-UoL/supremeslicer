from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, 
                             QMessageBox, QTextEdit, QMenuBar, QToolBar)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from lib.utils import Utils
from lib.main_engine import MainEngine
import sys


class SupremeSlicerUI(QMainWindow):
    """Main GUI Window for SupremeSlicer using PyQt5"""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.main_engine = MainEngine()

    def initUI(self):
        """Initialise the main window UI components."""
        self.setWindowTitle("SupremeSlicer GUI")
        self.setGeometry(100, 100, 800, 600)

        # Create a central text display area
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.setCentralWidget(self.text_display)

        self.createMenus() # Set up the Menu Bar


    def createMenus(self):
        """Create the main menu bar with various options."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        read_config_action = QAction('Read Config', self)
        read_config_action.triggered.connect(self.read_config)
        file_menu.addAction(read_config_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Information menu
        info_menu = menubar.addMenu('Information')

        show_doc_action = QAction('Show Documentation', self)
        show_doc_action.triggered.connect(self.show_documentation)
        info_menu.addAction(show_doc_action)

        output_part_info_action = QAction('Output Part Information', self)
        output_part_info_action.triggered.connect(self.get_part_info)
        info_menu.addAction(output_part_info_action)

        # Slicer menu
        slicer_menu = menubar.addMenu('Slicer')

        slice_action = QAction('Slice G-code File', self)
        slice_action.triggered.connect(self.run_slicer)
        slicer_menu.addAction(slice_action)

        stl_viewer_action = QAction('STL Viewer', self)
        stl_viewer_action.triggered.connect(self.run_stl_viewer)
        slicer_menu.addAction(stl_viewer_action)

        # Simulation menu
        simulation_menu = menubar.addMenu('Simulation')

        simulate_toolpath_action = QAction('Simulate Toolpath', self)
        simulate_toolpath_action.triggered.connect(self.run_simulation)
        simulation_menu.addAction(simulate_toolpath_action)

        render_mesh_simulation_action = QAction('Render Mesh Simulation', self)
        render_mesh_simulation_action.triggered.connect(self.run_animation)
        simulation_menu.addAction(render_mesh_simulation_action)

        # Toolbar menu
        toolbar_menu = menubar.addMenu('Toolbar')

        toolbar_menu_action = QAction('Vacuum Window', self)
        toolbar_menu_action.triggered.connect(self.run_vacuum_tool)
        toolbar_menu.addAction(toolbar_menu_action)


    def display_message(self, message):
        """Display messages in the central text area."""
        self.text_display.append(message + '\n')

#################################
    """ Methods for bridging main_engine functionality"""

    def read_config(self):
        """Open and display the config file."""
        try:
            config_data = Utils.read_yaml(Utils.get_resource_path(r'configs/config.yaml'))
            config_info = "\n".join([f"{k}: {v}" for k, v in config_data.items()])
            self.display_message("Config File:\n" + config_info)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading config file: {str(e)}")
            sys.exit()

    def run_slicer(self):
        """Run the slicer and display the result."""
        try:
            self.main_engine._run_slicer()
            self.display_message("G-code slicing completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running slicer: {str(e)}")
            sys.exit()

    def run_stl_viewer(self):
        """Run the STL viewer."""
        try:
            self.display_message("STL viewer started.")
            self.main_engine._run_stl_viewer()
            self.display_message("STL viewer closed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running STL viewer: {str(e)}")
            sys.exit()

    def get_part_info(self):
        """Obtain and display part information."""
        try:
            self.display_message("Getting part information")
            self.main_engine._get_part_info()
            self.display_message("Part information displayed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error getting part info: {str(e)}")
            sys.exit()

    def run_vacuum_tool(self):
        """Run the VacuumPnP tool."""
        try:
            self.display_message("Rendering vacuum_tool options")
            self.main_engine._vacuum_tool()
            self.display_message("VacuumPnP tool completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running VacuumPnP tool: {str(e)}")
            sys.exit()

    def run_simulation(self):
        """Run the simulation."""
        try:
            self.display_message("Rendering simulation window options.")
            self.main_engine._run_simulation()
            self.display_message("Simulation completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running simulation: {str(e)}")
            sys.exit()

    def run_animation(self):
        """Run the animation tool."""
        try:
            self.display_message("Obtaining animation render options")
            self.main_engine._run_animation()
            self.display_message("Animation rendering completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running animation: {str(e)}")
            sys.exit()

    def show_documentation(self):
        """Display the documentation."""
        doc_text = (
            "This tool was made by Pralish Satyal and can slice an STL, converting it to GCODE.\n"
            "It allows custom G-Code injection for custom tools such as the VacuumPnP.\n"
            "Custom tools include the general extruder, the VacuumPnP tool, the screwdriver, and the gripper."
        )
        QMessageBox.information(self, "Documentation", doc_text)
