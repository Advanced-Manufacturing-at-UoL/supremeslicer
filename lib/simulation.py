import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
import re
import time
import yaml

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

    def update_plot(self, num):
        """Update the plot with each new coordinate."""
        artists = []

        if hasattr(self, 'vacuum_coords_np'):
            vacuum_lines = self.vacuum_coords_np[:num]
            if hasattr(self, 'vacuum_line') and self.vacuum_line:
                self.vacuum_line.set_data(vacuum_lines[:, 0], vacuum_lines[:, 1])
                self.vacuum_line.set_3d_properties(vacuum_lines[:, 2])
                artists.append(self.vacuum_line)
            else:
                self.vacuum_line, = self.ax.plot(vacuum_lines[:, 0], vacuum_lines[:, 1], vacuum_lines[:, 2], color='blue')
                artists.append(self.vacuum_line)

        else:
            if not hasattr(self, 'lines'):
                self.lines = []

            for line in self.lines:
                line.set_data([], [])
                line.set_3d_properties([])
                artists.append(line)

            for i, segment in enumerate(self.segments[:num]):
                if segment:
                    x_vals, y_vals, z_vals = zip(*segment)
                    if i < len(self.lines):
                        line = self.lines[i]
                        line.set_data(x_vals, y_vals)
                        line.set_3d_properties(z_vals)
                        artists.append(line)
                    else:
                        line, = self.ax.plot(x_vals, y_vals, z_vals, color='b', lw=0.5)
                        self.lines.append(line)
                        artists.append(line)

            if self.show_travel:
                if hasattr(self, 'travel_line') and self.travel_line:
                    self.travel_line.set_data(self.travel_coords_np[:num, 0], self.travel_coords_np[:num, 1])
                    self.travel_line.set_3d_properties(self.travel_coords_np[:num, 2])
                    artists.append(self.travel_line)
                else:
                    travel_lines = self.travel_coords_np[:num]
                    if travel_lines.size:
                        x_vals, y_vals, z_vals = zip(*travel_lines)
                        self.travel_line, = self.ax.plot(x_vals, y_vals, z_vals, color='g', lw=0.5)
                        artists.append(self.travel_line)

            if self.vacuum_start_frame is not None and self.vacuum_end_frame is not None:
                if self.vacuum_start_frame <= num:
                    vacuum_segment = self.vacuum_coords[:num - self.vacuum_start_frame]
                    if vacuum_segment:
                        x_vals, y_vals, z_vals = zip(*vacuum_segment)
                        if hasattr(self, 'vacuum_line') and self.vacuum_line:
                            self.vacuum_line.set_data(x_vals, y_vals)
                            self.vacuum_line.set_3d_properties(z_vals)
                            artists.append(self.vacuum_line)
                        else:
                            self.vacuum_line, = self.ax.plot(x_vals, y_vals, z_vals, color='r', lw=0.5)
                            artists.append(self.vacuum_line)

        self.fig.canvas.draw_idle()
        return artists

    def update_slider(self, val):
        """Update the plot based on the slider value."""
        current_time = time.time()

        if current_time - int(self.last_slider_update) > self.slider_update_interval:
            self.last_slider_update = current_time
            try:
                frame = int(val)
            except ValueError:
                frame = 0
            self.update_plot(frame)
            self.fig.canvas.draw_idle()

    def play_animation(self, event):
        """Start or resume the animation from the current slider value."""
        if not self.animating:
            self.animating = True
            try:
                self.current_frame = int(self.slider.val)
            except ValueError:
                self.current_frame = 0
            if hasattr(self, 'ani'):
                self.ani.event_source.stop()
            self.ani = animation.FuncAnimation(
                self.fig, self.update_plot, frames=range(self.current_frame, len(self.segments)),
                interval=self.interval, blit=True, repeat=False
            )
            self.fig.canvas.draw_idle()
        else:
            self.ani.event_source.start()

    def pause_animation(self, event):
        """Pause the animation."""
        if self.animating:
            self.animating = False
            self.ani.event_source.stop()

    def forward_frame(self, event):
        """Move one frame forward."""
        current_val = self.slider.val
        try:
            new_val = min(int(current_val) + 1, self.slider.valmax)
        except ValueError:
            new_val = self.slider.valmax
        self.slider.set_val(new_val)
        self.current_frame = int(new_val)
        self.update_plot(self.current_frame)
        self.fig.canvas.draw_idle()

    def backward_frame(self, event):
        """Move one frame backward."""
        current_val = self.slider.val
        try:
            new_val = max(int(current_val) - 1, self.slider.valmin)
        except ValueError:
            new_val = self.slider.valmin
        self.slider.set_val(new_val)
        self.current_frame = int(new_val)
        self.update_plot(self.current_frame)
        self.fig.canvas.draw_idle()

    def plot_toolpath_animation(self, e_coords_list, travel_coords_list, coordinates, interval):
        """Animate the toolpath given a list of (command, x, y, z) coordinates."""
        self.common_e_coords_np = np.array([[x, y, z] for _, x, y, z, _ in e_coords_list])
        self.travel_coords_np = np.array([[x, y, z] for _, x, y, z, _ in travel_coords_list])
        self.coords_np = np.array([[x, y, z] for _, x, y, z, _, _ in coordinates])
        self.segments = self.split_into_segments(coordinates)
        num_frames = len(self.segments)
        self.interval = interval

        if num_frames == 0:
            print("No segments found in the G-code. Cannot create animation.")
            return

        # Parse and store vacuum coordinates
        vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()
        vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]
        _, _, vacuum_coordinates = self.parse_gcode(vacuum_gcode)
        self.vacuum_coords = [(x, y, z) for _, x, y, z, _, _ in vacuum_coordinates]

        # Set up the plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.lines = []
        self.ax.set_xlim([0, 180])
        self.ax.set_ylim([0, 180])
        self.ax.set_zlim([0, 100])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('G-code Toolpath Simulation')
        
        # Create playback controls
        ax_play = plt.axes([0.1, 0.02, 0.1, 0.075])
        ax_pause = plt.axes([0.22, 0.02, 0.1, 0.075])
        ax_forward = plt.axes([0.34, 0.02, 0.1, 0.075])
        ax_backward = plt.axes([0.46, 0.02, 0.1, 0.075])
        ax_slider = plt.axes([0.1, 0.09, 0.75, 0.03])

        btn_play = Button(ax_play, 'Play')
        btn_pause = Button(ax_pause, 'Pause')
        btn_forward = Button(ax_forward, 'Forward')
        btn_backward = Button(ax_backward, 'Backward')
        self.slider = Slider(ax_slider, 'Frame', 0, num_frames - 1, valinit=0, valstep=1)

        btn_play.on_clicked(self.play_animation)
        btn_pause.on_clicked(self.pause_animation)
        btn_forward.on_clicked(self.forward_frame)
        btn_backward.on_clicked(self.backward_frame)
        self.slider.on_changed(self.update_slider)

        plt.show()

    def plot_vacuum_animation(self, vacuum_coords, interval):
        """Animate the vacuum toolpath given a list of (x, y, z) coordinates."""
        self.vacuum_coords_np = np.array(vacuum_coords)
        self.segments = [vacuum_coords]  # Treat the entire vacuum path as a single segment
        num_frames = len(self.segments[0])  # Number of frames is the length of the vacuum path
        self.interval = interval

        if num_frames == 0:
            print("No segments found in the vacuum G-code. Cannot create animation.")
            return

        # Set up the plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.lines = []
        self.ax.set_xlim([0, 180])
        self.ax.set_ylim([0, 180])
        self.ax.set_zlim([0, 100])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('Vacuum G-code Toolpath Simulation')

        # Create playback controls
        ax_play = plt.axes([0.1, 0.02, 0.1, 0.075])
        ax_pause = plt.axes([0.22, 0.02, 0.1, 0.075])
        ax_forward = plt.axes([0.34, 0.02, 0.1, 0.075])
        ax_backward = plt.axes([0.46, 0.02, 0.1, 0.075])
        ax_slider = plt.axes([0.1, 0.09, 0.75, 0.03])

        btn_play = Button(ax_play, 'Play')
        btn_pause = Button(ax_pause, 'Pause')
        btn_forward = Button(ax_forward, 'Forward')
        btn_backward = Button(ax_backward, 'Backward')
        self.slider = Slider(ax_slider, 'Frame', 0, num_frames - 1, valinit=0, valstep=1)

        btn_play.on_clicked(self.play_animation)
        btn_pause.on_clicked(self.pause_animation)
        btn_forward.on_clicked(self.forward_frame)
        btn_backward.on_clicked(self.backward_frame)
        self.slider.on_changed(self.update_slider)

        plt.show()

    def plot_vacuum_toolpath(self):
        """Plot the vacuum toolpath from the G-code."""
        vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()

        if vacuum_start_line is not None and vacuum_end_line is not None:
            vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]
            _, _, vacuum_coordinates = self.parse_gcode(vacuum_gcode)
            vacuum_coords = [(x, y, z) for _, x, y, z, _, _ in vacuum_coordinates]
            self.plot_vacuum_animation(vacuum_coords, interval=50)
        else:
            print("No vacuum G-code found in the file.")

    def plot_original_toolpath(self):
        """Plot the original toolpath from the full G-code."""
        e_coords, travel_coords, coordinates = self.parse_gcode(self.gcode)

        if not coordinates:
            print("No coordinates found in the G-code.")
            return

        self.plot_toolpath_animation(e_coords, travel_coords, coordinates, interval=50)

    def create_line_number_mapping(self, filtered_lines):
        """Create a mapping of original line numbers to their indices in the filtered list."""
        line_number_to_index = {}
        current_line_number = 0

        for idx, line in enumerate(filtered_lines):
            if line.strip() and not line.strip().startswith(';'):
                current_line_number += 1
                line_number_to_index[current_line_number] = idx

        return line_number_to_index

    def get_vacuum_coordinates(self):
        """Find and print the coordinates corresponding to the vacuum PnP toolpath."""
        filtered_lines = [line.strip() for line in self.gcode if line.strip() and not line.strip().startswith(';')]
        line_number_to_index = self.create_line_number_mapping(filtered_lines)

        # Find the vacuum G-code lines
        vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()
        if vacuum_start_line is None or vacuum_end_line is None:
            print("No vacuum injection G-code found.")
            return

        # Parse the vacuum G-code to get coordinates
        vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]
        vacuum_coords = self.parse_gcode(vacuum_gcode)

        # Extract the original line numbers from the full G-code
        full_gcode_coords = self.parse_gcode(self.gcode)
        original_line_numbers = [coord[4] for coord in full_gcode_coords]

        # Map line numbers to frame indices
        line_number_to_frame = {line_number: idx for idx, (cmd, x, y, z, line_number) in enumerate(full_gcode_coords)}

        # Extract and print vacuum coordinates based on the frame indices
        vacuum_coords_frames = [(vac_coord[1], vac_coord[2], vac_coord[3])
                                for vac_coord in vacuum_coords
                                if vac_coord[4] in line_number_to_frame]

        print("Vacuum PnP Coordinates:")
        for frame in vacuum_coords_frames:
            print(f"X: {frame[0]}, Y: {frame[1]}, Z: {frame[2]}")

        return vacuum_coords_frames
