import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider

class SimulationProcessor:
    def __init__(self, filename):
        """Initialize class"""
        self.filename = filename
        self.gcode = self.read_gcode()
        self.animating = False
        self.current_frame = 0
        self.vacuum_start_frame = None
        self.vacuum_end_frame = None

    def read_gcode(self):
        """Read G-code from a file."""
        try:
            with open(self.filename, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            print(f"Error: File {self.filename} not found.")
            return []

    def find_vacuum_gcode_lines(self):
        """Find the start and end lines of the vacuum G-code in terms of relevant G-code commands."""
        start_comment = "; VacuumPnP TOOL G CODE INJECTION START"
        end_comment = "; VacuumPnP TOOL G CODE INJECTION END"

        start_line = end_line = None

        for i, line in enumerate(self.gcode):
            if start_comment in line:
                start_line = i
            if end_comment in line:
                end_line = i
                break

        return start_line, end_line

    def parse_gcode(self, gcode):
        """Parse G-code and return a list of (command, x, y, z) coordinates with their original line numbers."""
        coordinates = []
        e_coordinates = []
        x, y, z = 0.0, 0.0, 0.0

        for line_number, line in enumerate(gcode):
            line = line.strip()
            if not line or line.startswith(';'):
                continue # ignore comments

            parts = line.split()
            command = None
            contains_e = False
            # contains_e = any(part.startswith('E') for part in parts) # Check if line contains extrusion (E) as if it doesn't contain this skip

            for part in parts:
                if part.startswith('G'):
                    command = part
                elif part.startswith('X'):
                    try:
                        x = float(part[1:])
                    except ValueError:
                        x = 0.0
                elif part.startswith('Y'):
                    try:
                        y = float(part[1:])
                    except ValueError:
                        y = 0.0
                elif part.startswith('Z'):
                    try:
                        z = float(part[1:])
                    except ValueError:
                        z = 0.0
                elif part.startswith('E'):
                    contains_e = True
                    #contains_e # the command is a print command. Therefore, we want to append this to a list
                    #if command is not None:
                    #    e_coordinates.append((command, x, y, z, line_number))

            # G0 doesn't work as we only use this in vacuum tool. Therefore we just need to see if E is present
            if command is not None:
                if contains_e:
                    e_coordinates.append((command, x, y, z, line_number))
                else:
                    coordinates.append((command, x, y, z, line_number))
                
        return e_coordinates, coordinates

        # Add logic to say if the e_coordinates are also in the coordinates array then plot it. If they are not, do not connect those lines
        # common_e_coords = set(e_coordinates).intersection(set(coordinates))
        # common_e_coords_list = list(common_e_coords)

        # return common_e_coords_list, coordinates
        
    
        # interpolated_coords = []
        # e_interpolated_coords = []

        # for i in range(len(coordinates) - 1):
        #     cmd1, x1, y1, z1, ln1 = coordinates[i]
        #     cmd2, x2, y2, z2, ln2 = coordinates[i + 1]

        #     if cmd1.startswith('G0') and cmd2.startswith('G1') and contains_e:
        #         print(f"Command contains e: {cmd1} \n{cmd2}")
        #         num_steps = 1#0  # Adjust number of interpolation steps
        #         xs = np.linspace(x1, x2, num_steps)
        #         ys = np.linspace(y1, y2, num_steps)
        #         zs = np.linspace(z1, z2, num_steps)
        #         for j in range(num_steps):
        #             interpolated_coords.append(('G1', xs[j], ys[j], zs[j], ln1))
        #             interpolated
        #     else:
        #         interpolated_coords.append((cmd1, x1, y1, z1, ln1))

        # if coordinates:
        #     interpolated_coords.append(coordinates[-1])

        # return interpolated_coords

    def update_plot(self, num):
        """Update the plot with each new coordinate."""
        self.current_frame = num

        # Original line should be a scatter unless it's the normal line 
        self.scatter.set_data(self.coords_np[:, 0], self.coords_np[:, 1])
        self.scatter.set_3d_properties(self.coords_np[:, 2])

        # Update the blue line data
        self.line.set_data(self.coords_np[:num, 0], self.coords_np[:num, 1])
        self.line.set_3d_properties(self.coords_np[:num, 2])
        self.line.set_color('b')

        # Update the line plot for common_e_coords_list
        if self.common_e_coords_np.size > 0:
            if num > 0:
                self.line.set_data(self.common_e_coords_np[:num, 0], self.common_e_coords_np[:num, 1])
                self.line.set_3d_properties(self.common_e_coords_np[:num, 2])
            else:
                self.line.set_data([], [])
                self.line.set_3d_properties([])

        # Update vacuum line data
        if self.vacuum_start_frame is not None and self.vacuum_end_frame is not None:
            if self.vacuum_start_frame <= num <= self.vacuum_end_frame:
                vacuum_num = num - self.vacuum_start_frame
                self.vacuum_line.set_data(self.vacuum_coords_np[:vacuum_num, 0], self.vacuum_coords_np[:vacuum_num, 1])
                self.vacuum_line.set_3d_properties(self.vacuum_coords_np[:vacuum_num, 2])
                self.vacuum_line.set_color('r')
            elif num > self.vacuum_end_frame:
                self.vacuum_line.set_data(self.vacuum_coords_np[:, 0], self.vacuum_coords_np[:, 1])
                self.vacuum_line.set_3d_properties(self.vacuum_coords_np[:, 2])
                self.vacuum_line.set_color('r')
            else:
                self.vacuum_line.set_data([], [])
                self.vacuum_line.set_3d_properties([])
        else:
            self.vacuum_line.set_data([], [])
            self.vacuum_line.set_3d_properties([])

        # Update slider value conditionally
        if self.slider.val != num:
            self.slider.set_val(num)
        
        self.fig.canvas.draw_idle()
        return self.line, self.vacuum_line, self.scatter

    def update_slider(self, val):
        """Update the plot based on the slider value."""
        frame = int(val)
        self.update_plot(frame)
        self.fig.canvas.draw_idle()

    def play_animation(self, event):
        """Start or resume the animation from the current slider value."""
        if not self.animating:
            self.animating = True
            self.current_frame = int(self.slider.val)
            if hasattr(self, 'ani'):
                self.ani.event_source.stop()
            self.ani = animation.FuncAnimation(
                self.fig, self.update_plot, frames=range(self.current_frame, len(self.coords_np)),
                interval=self.interval, blit=False, repeat=False
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
        new_val = min(current_val + 1, self.slider.valmax)
        self.slider.set_val(new_val)
        self.current_frame = int(new_val)
        self.update_plot(self.current_frame)
        self.fig.canvas.draw_idle()

    def backward_frame(self, event):
        """Move one frame backward."""
        current_val = self.slider.val
        new_val = max(current_val - 1, self.slider.valmin)
        self.slider.set_val(new_val)
        self.current_frame = int(new_val)
        self.update_plot(self.current_frame)
        self.fig.canvas.draw_idle()

    def plot_toolpath_animation(self, common_e_coords_list, coordinates, interval):
        """Animate the toolpath given a list of (command, x, y, z) coordinates."""
        # if not common_e_coords_list and not coordinates:
        #     print("No coordinates to animate.")
        #     return

        print("Printing common e coords list\n")
        print(common_e_coords_list)
        print("Printing coordinates list")
        print(coordinates)
        # Extract coordinates
        if common_e_coords_list:
            self.common_e_coords_np = np.array([[x, y, z] for _, x, y, z, _ in common_e_coords_list])
        else:
            self.common_e_coords_np = np.empty((0, 3))
        
        self.coords_np = np.array([[x, y, z] for _, x, y, z, _ in coordinates])
        num_frames = len(self.coords_np)
        self.interval = interval

        # Set up the plot
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111, projection='3d')
        self.line, = ax.plot([], [], [], lw=0.5, color='g')  # Default color
        self.vacuum_line, = ax.plot([], [], [], lw=0.5, color='r')  # Red for vacuum toolpath

        # Create scatter plot for coordinates
        self.scatter = ax.scatter(self.coords_np[:, 0], self.coords_np[:, 1], self.coords_np[:, 2], c='b', marker='o')  # Blue for scatter
        
        ax.set_xlim([0, 180])
        ax.set_ylim([0, 180])
        ax.set_zlim([0, 100])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('G-code Toolpath Simulation')

        def init():
            self.line.set_data([], [])
            self.line.set_3d_properties([])
            self.vacuum_line.set_data([], [])
            self.vacuum_line.set_3d_properties([])
            return self.line, self.vacuum_line, self.scatter

        init()

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


    def plot_original_toolpath(self):
        """Plot the original toolpath from the full G-code."""
        coordinates, e_coordinates = self.parse_gcode(self.gcode)
        print("Within plot_original_toolpath we are reading gcode and printing coordinates\n")
        print(coordinates)
        print("Now printing e coordinates")
        print(e_coordinates)
        self.plot_toolpath_animation(coordinates, e_coordinates,interval=50)

    def plot_vacuum_toolpath(self):
        """Plot the vacuum toolpath from the G-code."""
        vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()
        if vacuum_start_line is not None and vacuum_end_line is not None:
            vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]
            coordinates = self.parse_gcode(vacuum_gcode)
            self.plot_toolpath_animation(coordinates, interval=50)
        else:
            print("No vacuum injection G-code found.")

    def create_line_number_mapping(self, filtered_lines):
        """Create a mapping of original line numbers to their indices in the filtered list."""
        line_number_to_index = {}
        current_line_number = 0

        for line in filtered_lines:
            if line.strip() and not line.strip().startswith(';'):
                current_line_number += 1
                line_number_to_index[current_line_number] = len(line_number_to_index)
        
        return line_number_to_index

    def get_vacuum_coordinates(self):
        """Find and print the coordinates corresponding to the vacuum PnP toolpath."""
        # Filtered G-code lines and create mapping
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

    def find_index_in_original_line_numbers(self, original_line_numbers, target_line_number):
        """Find the index of the target line number in the list of original line numbers."""
        try:
            return original_line_numbers.index(target_line_number)
        except ValueError:
            print(f"Line number {target_line_number} not found in the original line numbers.")
            return None

    def plot_original_toolpath(self):
        """Plot the original toolpath from the full G-code."""
        common_e_coords_list, coordinates = self.parse_gcode(self.gcode)
        self.plot_toolpath_animation(common_e_coords_list, coordinates, interval=50)