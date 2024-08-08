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
        self.show_travel = self.config.get('show_travel', 0)  # Flag from YAML configuration

    def load_config(self):
        """Load configuration from a YAML file."""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: Configuration file {self.config_file} not found.")

    def read_gcode(self):
        """Read G-code from a file."""
        try:
            with open(self.filename, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File {self.filename} not found.")

    def parse_gcode(self, gcode):
        """Parse G-code and return lists of extrusion and travel coordinates."""
        e_coordinates = []  # Commands with extrusion
        travel_coordinates = [] # Just the travel commands
        coordinates = []    # All commands

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
        """Animate the toolpath given a list of (command, x, y, z) coordinates."""

        try:
            common_e_coords_np = np.array([[x, y, z] for _, x, y, z, _ in e_coords_list])
            travel_coords = np.array([[x, y, z] for _, x, y, z, _ in travel_coords_list])
            coords = np.array([[x, y, z] for _, x, y, z, _, _ in coordinates])

            self.segments = self.split_into_segments(coordinates)
            num_frames = len(self.segments)
            self.interval = interval

            if num_frames == 0:
                print("No segments found in the G-code. Cannot create animation.")
                return

            # Set up the PyVista plot
            plotter = pv.Plotter()
            plotter.set_background('white')  # Use set_background instead of add_background

            # Initialize data for animation
            self.plotter = plotter
            self.num_frames = num_frames
            self.current_frame = 0

            def update_frame(frame):
                """Update the plot with each frame."""
                self.current_frame = frame
                plotter.clear()
                # Draw the toolpath segments up to the current frame
                for segment in self.segments[:frame]:
                    if segment:
                        plotter.add_lines(np.array(segment), color='blue')
                if self.show_travel:
                    travel_lines = travel_coords[:frame]
                    if len(travel_lines):
                        plotter.add_lines(travel_lines, color='green')
                plotter.update()

            def animate():
                """Perform the animation."""
                for frame in range(self.num_frames):
                    update_frame(frame)
                    plotter.render()  # Render the frame
                    time.sleep(self.interval / 1000.0)  # Adjust frame rate

            # Set up the interactive loop and animation
            plotter.add_callback(animate)
            plotter.show(auto_close=False)  # This should handle the interactive event loop internally

        except Exception as e:
            print("Error within plot_toolpath_animation")
            print(f"Error occurred: {e}")

    def plot_vacuum_animation(self, vacuum_coords, interval):
        """Animate the vacuum toolpath given a list of (x, y, z) coordinates."""

        try:
            self.vacuum_coords_np = np.array(vacuum_coords)
            self.segments = [vacuum_coords]  # Treat the entire vacuum path as a single segment
            num_frames = len(self.segments[0])  # Number of frames is the length of the vacuum path
            self.interval = interval

            if num_frames == 0:
                print("No segments found in the vacuum G-code. Cannot create animation.")
                return

            # Set up the PyVista plot
            plotter = pv.Plotter()
            plotter.set_background('white')  # Use set_background instead of add_background

            # Initialize data for animation
            self.plotter = plotter
            self.num_frames = num_frames
            self.current_frame = 0

            def update_frame(frame):
                """Update the plot with each frame."""
                self.current_frame = frame
                plotter.clear()
                vacuum_path = self.vacuum_coords_np[:frame]
                plotter.add_lines(vacuum_path, color='red')
                plotter.update()

            def animate():
                """Perform the animation."""
                for frame in range(self.num_frames):
                    update_frame(frame)
                    plotter.render()  # Render the frame
                    time.sleep(self.interval / 1000.0)  # Adjust frame rate

            # Set up the interactive loop and animation
            plotter.add_callback(animate)
            plotter.show(auto_close=False)  # This should handle the interactive event loop internally

        except Exception as e:
            print("Error within plot_vacuum_animation")
            print(f"Error occurred: {e}")

    def plot_vacuum_toolpath(self):
        """Plot the vacuum toolpath from the G-code."""
        vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()
        try:
            if vacuum_start_line is not None and vacuum_end_line is not None:
                vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]
                _, _, vacuum_coordinates = self.parse_gcode(vacuum_gcode)
                vacuum_coords = [(x, y, z) for _, x, y, z, _, _ in vacuum_coordinates]
                self.plot_vacuum_animation(vacuum_coords, interval=50)
            else:
                print("No vacuum G-code found in the file.")
        except Exception as e:
            print("Error within plot_vacuum_toolpath")
            print(f"Error occurred: {e}")

    def plot_original_toolpath(self):
        """Plot the original toolpath from the full G-code."""
        e_coords, travel_coords, coordinates = self.parse_gcode(self.gcode)
        try:
            if not coordinates:
                print("No coordinates found in the G-code.")
                return
            self.plot_toolpath_animation(e_coords, travel_coords, coordinates, interval=50)
        except Exception as e:
            print("Error within plot_original_toolpath")
            print(f"Error occurred: {e}")

    def find_vacuum_gcode_lines(self):
        """Find the lines of G-code related to vacuum operations."""
        start_line = None
        end_line = None
        for i, line in enumerate(self.gcode):
            if 'VACUUM_START' in line:
                start_line = i
            if 'VACUUM_END' in line:
                end_line = i
                break
        return start_line, end_line

    def process_simulation(self, interval=100):
        """Process the G-code and generate the animation."""
        e_coords_list, travel_coords_list, coordinates = self.parse_gcode(self.gcode)
        self.plot_toolpath_animation(e_coords_list, travel_coords_list, coordinates, interval)

# Example usage
if __name__ == "__main__":
    sim_processor = SimulationProcessor(r'output\benchy.gcode')
    sim_processor.process_simulation(interval=100)
