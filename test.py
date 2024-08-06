import numpy as np
import re
import time
import yaml
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.validators.scatter.marker import SymbolValidator
import plotly.graph_objs as go

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

    def load_config(self):
        """Load configuration from a YAML file."""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file {self.config_file} not found.")
            return {}

    def read_gcode(self):
        """Read G-code from a file."""
        try:
            with open(self.filename, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            print(f"Error: File {self.filename} not found.")
            return []

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
        travel_coordinates = []  # Just the travel commands

        x, y, z = 0.0, 0.0, 0.0
        command_pattern = re.compile(r'([G]\d+)')
        coordinate_pattern = re.compile(r'(X[-\d.]+|Y[-\d.]+|Z[-\d.]+|E[-\d.]+)')

        for line_number, line in enumerate(gcode):
            line = line.strip()
            if not line or line.startswith(';'):
                continue  # ignore comments

            command_match = command_pattern.search(line)
            command = command_match.group(1) if command_match else None

            coords = coordinate_pattern.findall(line)
            contains_e = any(c.startswith('E') for c in coords)

            for coord in coords:
                if coord.startswith('X'):
                    x = float(coord[1:])
                elif coord.startswith('Y'):
                    y = float(coord[1:])
                elif coord.startswith('Z'):
                    z = float(coord[1:])
                elif coord.startswith('E'):
                    contains_e = True

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

    def update_plot(self, frame):
        """Update the plot with each new coordinate."""
        self.current_frame = frame

        # Extract the current segments up to the current frame
        current_segments = self.segments[:frame]

        traces = []

        # Plot the segments
        for segment in current_segments:
            if segment:  # Ensure the segment is not empty
                x_vals, y_vals, z_vals = zip(*segment)
                traces.append(go.Scatter3d(x=x_vals, y=y_vals, z=z_vals, mode='lines', line=dict(color='blue', width=2)))

        # Plot the travel lines if the flag is set
        if self.show_travel:
            travel_lines = self.travel_coords_np[:frame]
            if len(travel_lines) > 0:
                x_vals, y_vals, z_vals = zip(*travel_lines)
                traces.append(go.Scatter3d(x=x_vals, y=y_vals, z=z_vals, mode='lines', line=dict(color='green', width=2)))

        # Plot the vacuum line if within the range
        if self.vacuum_start_frame is not None and self.vacuum_end_frame is not None:
            if self.vacuum_start_frame <= frame:
                vacuum_segment = self.vacuum_coords[:frame - self.vacuum_start_frame]
                if vacuum_segment:
                    x_vals, y_vals, z_vals = zip(*vacuum_segment)
                    traces.append(go.Scatter3d(x=x_vals, y=y_vals, z=z_vals, mode='lines', line=dict(color='red', width=2)))

        return traces

    def create_animation(self, frames, interval):
        print("\n~~Within create_animation~~")
        print("Creating figure")
        fig = go.Figure(
            frames=[go.Frame(data=self.update_plot(frame)) for frame in range(frames)]
        )
        print("Updating layout")
        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[0, 180], autorange=False),
                yaxis=dict(range=[0, 180], autorange=False),
                zaxis=dict(range=[0, 100], autorange=False),
                aspectmode='cube'
            ),
            updatemenus=[dict(
                type='buttons',
                showactive=False,
                buttons=[
                    dict(label='Play',
                         method='animate',
                         args=[None, dict(frame=dict(duration=interval, redraw=True), fromcurrent=True)]),
                    dict(label='Pause',
                         method='animate',
                         args=[[None], dict(frame=dict(duration=0, redraw=True), mode='immediate', fromcurrent=True)]),
                ]
            )]
        )
        print("Showing Figure")
        fig.show()
        print("Finished showing figure")

    def plot_toolpath_animation(self, e_coords_list, travel_coords_list, coordinates, interval):
        """Animate the toolpath given a list of (command, x, y, z) coordinates."""
        self.common_e_coords_np = np.array([[x, y, z] for _, x, y, z, _ in e_coords_list])
        self.travel_coords_np = np.array([[x, y, z] for _, x, y, z, _ in travel_coords_list])
        self.coords_np = np.array([[x, y, z] for _, x, y, z, _, _ in coordinates])
        self.segments = self.split_into_segments(coordinates)
        num_frames = len(self.segments)
        self.interval = interval

        print("within the plot toolpath animation")

        if num_frames == 0:
            print("No segments found in the G-code. Cannot create animation.")
            return
        
        # Parse and store vacuum coordinates
        print("finding vacuum Gcode Lines")
        vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()
        vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]

        print("parsing vacuum gcode")
        _, _, vacuum_coordinates = self.parse_gcode(vacuum_gcode)
        self.vacuum_coords = [(x, y, z) for _, x, y, z, _, _ in vacuum_coordinates]

        # Create and show animation
        print("creating animation")
        self.create_animation(num_frames, interval)

    def plot_vacuum_animation(self, vacuum_coords, interval):
        """Animate the vacuum toolpath given a list of (x, y, z) coordinates."""
        self.vacuum_coords_np = np.array(vacuum_coords)
        self.segments = [vacuum_coords]  # Treat the entire vacuum path as a single segment
        num_frames = len(self.segments[0])  # Number of frames is the length of the vacuum path
        self.interval = interval

        print("within the plot vacuum animation")

        if num_frames == 0:
            print("No segments found in the vacuum G-code. Cannot create animation.")
            return

        # Create and show animation
        self.create_animation(num_frames, interval)

    def plot_vacuum_toolpath(self):
        """Plot the vacuum toolpath from the G-code."""
        # Parse and store vacuum coordinates
        vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()
        if vacuum_start_line is not None and vacuum_end_line is not None:
            vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]
            _, _, vacuum_coordinates = self.parse_gcode(vacuum_gcode)
            vacuum_coords = [(x, y, z) for _, x, y, z, _, _ in vacuum_coordinates]

            # Plot the vacuum animation
            self.plot_vacuum_animation(vacuum_coords, interval=20)
        else:
            print("Vacuum G-code start or end line not found.")

def main():
    """Main function to create and show the G-code simulation."""
    filename = r'output\benchy.gcode'
    simulation_processor = SimulationProcessor(filename)

    e_coords_list, travel_coords_list, coordinates = simulation_processor.parse_gcode(simulation_processor.gcode)
    simulation_processor.plot_toolpath_animation(e_coords_list, travel_coords_list, coordinates, interval=10)
    simulation_processor.plot_vacuum_toolpath()

if __name__ == "__main__":
    main()
