import pyvista as pv
import numpy as np
import re
import yaml
import time

class SimulationProcessor:
    def __init__(self, filename):
        """Initialize class"""
        self.config_file = 'configs/simulation.yaml'
        self.filename = filename
        self.config = self.load_config()
        self.gcode = self.read_gcode()
        self.animating = False
        self.current_frame = 0
        self.vacuum_start_frame = None
        self.vacuum_end_frame = None
        self.vacuum_coords = []
        self.show_travel = self.config.get('show_travel', 0)  # Flag from YAML configuration
        self.last_slider_update = time.time()
        self.slider_update_interval = 0.1
        self.is_mesh_displayed = False  # New attribute to track mesh display

    def load_config(self):
        """Load configuration from a YAML file."""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise(f"Error: Configuration file {self.config_file} not found.")

    def read_gcode(self):
        """Read G-code from a file."""
        try:
            with open(self.filename, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            raise(f"Error: File {self.filename} not found.")

    def find_vacuum_gcode_lines(self):
        """Find the start and end lines of the vacuum G-code."""
        start_comment = "; VacuumPnP TOOL G CODE INJECTION START"
        end_comment = "; VacuumPnP TOOL G CODE INJECTION END"

        start_line = end_line = None

        for i, line in enumerate(self.gcode):
            if start_comment in line:
                start_line = i
            if end_comment in line:
                end_line = i
                break

        if start_line is not None and end_line is not None:
            self.vacuum_start_frame = start_line
            self.vacuum_end_frame = end_line

        return start_line, end_line

    def parse_gcode(self, gcode):
        """Parse G-code and return lists of extrusion and travel coordinates."""
        e_coordinates = []  # Commands with extrusion
        coordinates = []    # All commands
        travel_coordinates = [] # Just the travel commands

        x, y, z = 0.0, 0.0, 0.0
        command_pattern = re.compile(r'([G]\d+)')
        coordinate_pattern = re.compile(r'(X[-\d.]+|Y[-\d.]+|Z[-\d.]+|E[-\d.]+)')

        for line_number, line in enumerate(gcode):
            line = line.strip()
            if not line or line.startswith(';'):
                continue  # Ignore comments

            command_match = command_pattern.search(line)
            command = command_match.group(1) if command_match else None

            coords = coordinate_pattern.findall(line)
            contains_e = any(c.startswith('E') for c in coords)

            for coord in coords:
                try:
                    if coord.startswith('X'):
                        x = float(coord[1:])
                    elif coord.startswith('Y'):
                        y = float(coord[1:])
                    elif coord.startswith('Z'):
                        z = float(coord[1:])
                    elif coord.startswith('E'):
                        contains_e = True
                except ValueError:
                    print(f"Error parsing coordinate: {coord}")

            if command and (command == 'G0' or command == 'G1'):
                if contains_e:
                    e_coordinates.append((command, x, y, z, line_number))
                else:
                    travel_coordinates.append((command, x, y, z, line_number))
                coordinates.append((command, x, y, z, contains_e, line_number))

        return e_coordinates, travel_coordinates, coordinates

    def split_into_segments(self, coordinates):
        """Split coordinates into individual segments based on extrusion commands."""
        segments = []
        current_segment = []

        for command, x, y, z, contains_e, _ in coordinates:
            if contains_e:
                current_segment.append((x, y, z))
            elif current_segment:
                segments.append(current_segment)
                current_segment = []

        if current_segment:
            segments.append(current_segment)

        return segments

    def plot_toolpath_animation(self, e_coords_list, travel_coords_list, coordinates, interval):
        """Animate the toolpath given a list of (command, x, y, z) coordinates using PyVista."""

        try:
            # Apply the filter before abstracting values below
            f_coords = filter_close_coordinates(coordinates)
            f_ecoords = filter_close_coordinates(e_coords_list)
            f_travel_coords = filter_close_coordinates(travel_coords_list)

            common_e_coords_np = np.array([[x, y, z] for _, x, y, z, _ in f_ecoords])
            travel_coords = np.array([[x, y, z] for _, x, y, z, _ in f_travel_coords])
            coords = np.array([[x, y, z] for _, x, y, z, _, _ in f_coords])
            
            # Apply the filter just once, to filter the entire coordinates list
            self.common_e_coords_np = common_e_coords_np
            self.travel_coords_np = travel_coords
            self.coords_np = coords

            self.segments = self.split_into_segments(f_coords)
            num_frames = len(self.segments)
            self.interval = interval
            
            if num_frames == 0:
                print("No segments found in the G-code. Cannot create animation.")
                return

            # Parse and store vacuum coordinates
            vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()
            vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]
            _, _, vacuum_coordinates = self.parse_gcode(vacuum_gcode)
            self.vacuum_coords = np.array([[x, y, z] for _, x, y, z, _, _ in vacuum_coordinates])

            # Initialize PyVista plotter
            self.plotter = pv.Plotter()
            self.plotter.add_axes()

            # Define color and opacity for the toolpath
            self.line_color = 'blue'
            self.line_opacity = 0.6

            self.show_toolpath_animation()

        except Exception as e:
            print("Within plot_toolpath_animation")
            print(f"Error occurred: {e}")

    def show_toolpath_animation(self):
        """Render the toolpath animation with PyVista."""

        def update_frame(frame):
            self.plotter.clear()
            if self.is_mesh_displayed:
                # Show mesh
                x_vals, y_vals, z_vals = zip(*self.coords_np[:frame])
                self.plotter.add_mesh(pv.PolyData(np.array([x_vals, y_vals, z_vals]).T), color=self.line_color, opacity=self.line_opacity)
            else:
                # Show lines
                for segment in self.segments[:frame]:
                    if segment:
                        x_vals, y_vals, z_vals = zip(*segment)
                        self.plotter.add_lines(np.array([x_vals, y_vals, z_vals]).T, color=self.line_color, width=2)

            # Show travel path if enabled
            if self.show_travel:
                travel_coords = self.travel_coords_np[:frame]
                if len(travel_coords):
                    x_vals, y_vals, z_vals = zip(*travel_coords)
                    self.plotter.add_lines(np.array([x_vals, y_vals, z_vals]).T, color='green', width=2)

            self.plotter.render()

        # Animation setup
        self.plotter.open_gl_window()
        self.plotter.add_callback(update_frame)
        self.plotter.show()

    def plot_vacuum_animation(self, vacuum_coords, interval):
        """Animate the vacuum toolpath using PyVista."""

        try:
            self.vacuum_coords_np = np.array(vacuum_coords)
            self.segments = [vacuum_coords]  # Treat the entire vacuum path as a single segment
            num_frames = len(self.segments[0])  # Number of frames is the length of the vacuum path
            self.interval = interval

            if num_frames == 0:
                print("No segments found in the vacuum G-code. Cannot create animation.")
                return

            # Initialize PyVista plotter
            self.plotter = pv.Plotter()
            self.plotter.add_axes()

            # Define color and opacity for the vacuum toolpath
            self.line_color = 'red'
            self.line_opacity = 0.6

            self.show_vacuum_animation()

        except Exception as e:
            print("Within plot_vacuum_animation")
            print(f"Error occurred: {e}")

    def show_vacuum_animation(self):
        """Render the vacuum toolpath animation with PyVista."""

        def update_frame(frame):
            self.plotter.clear()
            # Show vacuum path
            if self.vacuum_coords_np is not None:
                x_vals, y_vals, z_vals = zip(*self.vacuum_coords_np[:frame])
                self.plotter.add_mesh(pv.PolyData(np.array([x_vals, y_vals, z_vals]).T), color=self.line_color, opacity=self.line_opacity)

            self.plotter.render()

        # Animation setup
        self.plotter.open_gl_window()
        self.plotter.add_callback(update_frame)
        self.plotter.show()

# Sample usage:
processor = SimulationProcessor(r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\supremeslicer\output\benchy.gcode')
e_coords, travel_coords, coordinates = processor.parse_gcode(processor.gcode)
processor.plot_toolpath_animation(e_coords, travel_coords, coordinates, interval=0.05)
processor.plot_vacuum_animation(processor.vacuum_coords, interval=0.05)
