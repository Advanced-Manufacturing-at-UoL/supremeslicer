import numpy as np
import re
import time
import yaml
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

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

        self.line_segments = []  # To store the line segments for animation

        # Initialize the plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

        self.ax.set_xlim([0, 180])
        self.ax.set_ylim([0, 180])
        self.ax.set_zlim([0, 100])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('G-code Toolpath Simulation')

        # Initialize empty line segments
        self.travel_line, = self.ax.plot([], [], [], color='g', lw=0.5) if self.show_travel else (None,)
        self.vacuum_line, = self.ax.plot([], [], [], color='r', lw=0.5)

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

    def update_plot(self, num):
        """Update the plot with each new coordinate."""
        self.current_frame = num

        # Update the segments up to the current frame
        for i, segment in enumerate(self.segments[:num]):
            if i < len(self.line_segments):
                if segment:  # Ensure the segment is not empty
                    x_vals, y_vals, z_vals = zip(*segment)
                    self.line_segments[i].set_data(x_vals, y_vals)
                    self.line_segments[i].set_3d_properties(z_vals)
            else:
                print(f"Warning: Segment index {i} out of range for line segments.")

        # Update the travel lines if the flag is set
        if self.show_travel:
            travel_lines = self.travel_coords_np[:num]
            if len(travel_lines) > 0:
                x_vals, y_vals, z_vals = zip(*travel_lines)
                self.travel_line.set_data(x_vals, y_vals)
                self.travel_line.set_3d_properties(z_vals)

        # Update the vacuum line if within the range
        if self.vacuum_start_frame is not None and self.vacuum_end_frame is not None:
            if self.vacuum_start_frame <= num:
                vacuum_segment = self.vacuum_coords[:num - self.vacuum_start_frame]
                if vacuum_segment:
                    x_vals, y_vals, z_vals = zip(*vacuum_segment)
                    self.vacuum_line.set_data(x_vals, y_vals)
                    self.vacuum_line.set_3d_properties(z_vals)

        return self.line_segments

    def create_animation(self, frames, interval):
        """Create animation and measure time taken."""
        start_time = time.time()  # Start timing
        
        print("\n~~Within create_animation~~")
        print("Creating figure")

        # Adjust line segments based on the number of frames
        print(f"Total number of frames{frames}")
        if len(self.line_segments) < frames:
            print(f"Line segments {len(self.line_segments)} is smaller than frames {frames} ")
            additional_lines_needed = frames - len(self.line_segments)

            for _ in range(additional_lines_needed):
                print("Inside for loop")
                line, = self.ax.plot([], [], [], color='b', lw=0.5)
                self.line_segments.append(line)

        # Use FuncAnimation to handle the animation
        def animate(num):
            print("Animate function called")
            self.update_plot(num)
            return self.line_segments + ([self.travel_line] if self.show_travel else []) + [self.vacuum_line]

        print("FuncAnimation called")
        anim = FuncAnimation(self.fig, animate, frames=frames, interval=interval, blit=True)

        # Save the animation using PillowWriter
        print("Saving as gif")
        anim.save('toolpath_animation.gif', writer=PillowWriter(fps=30))
        
        end_time = time.time()  # End timing
        print("Animation created")
        print(f"Time taken to create the animation: {end_time - start_time:.2f} seconds")

    def save_animation(self, filename, format='gif'):
        """Save the animation to a file."""
        if format == 'gif':
            writer = PillowWriter(fps=30)
        elif format == 'mp4':
            writer = FFMpegWriter(fps=30)
        else:
            raise ValueError("Unsupported format. Use 'gif' or 'mp4'.")

        self.anim.save(filename, writer=writer)
        print(f"Animation saved as {filename}")

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
        vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1] if vacuum_start_line is not None and vacuum_end_line is not None else []
        _, _, vacuum_coordinates = self.parse_gcode(vacuum_gcode)
        self.vacuum_coords = [(x, y, z) for _, x, y, z, _, _ in vacuum_coordinates]

        # Initialize empty lines in the plot
        self.line_segments = [self.ax.plot([], [], [], color='b', lw=0.5)[0] for _ in self.segments]

        # Create animation
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

        # Create animation
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
    filename = r'output/benchy.gcode'
    simulation_processor = SimulationProcessor(filename)

    print("Obtaining coordinates in main")
    e_coords_list, travel_coords_list, coordinates = simulation_processor.parse_gcode(simulation_processor.gcode)
    print("Obtaining simulation in main")
    simulation_processor.plot_toolpath_animation(e_coords_list, travel_coords_list, coordinates, interval=10)
    print("Saving as GIF")
    simulation_processor.save_animation('toolpath_animation.gif', format='gif')
    print("Saving as MP4")
    simulation_processor.save_animation('toolpath_animation.mp4', format='mp4')

if __name__ == "__main__":
    main()
