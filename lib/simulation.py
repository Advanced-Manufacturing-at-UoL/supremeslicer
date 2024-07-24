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
        with open(self.filename, 'r') as f:
            return f.readlines()

    def find_vacuum_gcode_lines(self):
        """Find the start and end lines of the vacuum G-code in terms of relevant G-code commands."""
        start_comment = "; VacuumPnP TOOL G CODE INJECTION START"
        end_comment = "; VacuumPnP TOOL G CODE INJECTION END"

        start_line = None
        end_line = None

        command_lines = [i for i, line in enumerate(self.gcode) if line.strip() and not line.strip().startswith(';')]

        for i in command_lines:
            line = self.gcode[i]
            if start_comment in line:
                start_line = i
            if end_comment in line:
                end_line = i
                break
            
        return start_line, end_line

    def parse_gcode(self, gcode):
        """Parse G-code and return a list of (command, x, y, z) coordinates with their original line numbers."""
        coordinates = []
        x, y, z = 0.0, 0.0, 0.0

        for line_number, line in enumerate(gcode):
            line = line.strip()
            if not line or line.startswith(';'):
                continue

            parts = line.split()
            command = None
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

            if command is not None:
                coordinates.append((command, x, y, z, line_number))

        interpolated_coords = []
        for i in range(len(coordinates) - 1):
            cmd1, x1, y1, z1, ln1 = coordinates[i]
            cmd2, x2, y2, z2, ln2 = coordinates[i + 1]

            if cmd1.startswith('G0') and cmd2.startswith('G1'):
                num_steps = 10  # Adjust number of interpolation steps
                xs = np.linspace(x1, x2, num_steps)
                ys = np.linspace(y1, y2, num_steps)
                zs = np.linspace(z1, z2, num_steps)

                for j in range(num_steps):
                    interpolated_coords.append(('G1', xs[j], ys[j], zs[j], ln1))
            else:
                interpolated_coords.append((cmd1, x1, y1, z1, ln1))

        if coordinates:
            interpolated_coords.append(coordinates[-1])

        return interpolated_coords


    def update_plot(self, num):
        """Update the plot with each new coordinate."""
        self.current_frame = num
        self.line.set_data(self.coords_np[:num, 0], self.coords_np[:num, 1])
        self.line.set_3d_properties(self.coords_np[:num, 2])

        # Highlight vacuum tool usage coordinates
        if self.vacuum_start_frame is not None and self.vacuum_end_frame is not None:
            if self.vacuum_start_frame <= num <= self.vacuum_end_frame:
                self.line.set_color('r')
            else:
                self.line.set_color('b')
        else:
            self.line.set_color('b')

        return self.line,

    def update_slider(self, val):
        """Update the plot based on the slider value."""
        frame = int(val)
        self.current_frame = frame
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

    def plot_toolpath_animation(self, coordinates, interval):
        """Animate the toolpath given a list of (command, x, y, z) coordinates."""
        if not coordinates:
            print("No coordinates to animate.")
            return

        # Find vacuum G-code lines
        vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()
        vacuum_coords = []

        if vacuum_start_line is not None and vacuum_end_line is not None:
            vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]
            vacuum_coords = self.parse_gcode(vacuum_gcode)

        # Extract the original line numbers from the parsed coordinates
        original_line_numbers = [coord[4] for coord in coordinates]

        # Initialize vacuum injection start and end frames
        self.vacuum_start_frame = None
        self.vacuum_end_frame = None

        # Find the frame numbers for vacuum injection start and end
        if vacuum_coords:
            first_vacuum_line_number = vacuum_coords[0][4]
            last_vacuum_line_number = vacuum_coords[-1][4]

            if first_vacuum_line_number in original_line_numbers:
                self.vacuum_start_frame = original_line_numbers.index(first_vacuum_line_number)
            if last_vacuum_line_number in original_line_numbers:
                self.vacuum_end_frame = original_line_numbers.index(last_vacuum_line_number)

        print(f"Vacuum injection starts at frame: {self.vacuum_start_frame}")
        print(f"Vacuum injection ends at frame: {self.vacuum_end_frame}")

        self.fig = plt.figure()
        ax = self.fig.add_subplot(111, projection='3d')
        self.coords_np = np.array([[x, y, z] for _, x, y, z, _ in coordinates])
        num_frames = len(self.coords_np)
        self.interval = interval

        # Plot only once
        self.line, = ax.plot([], [], [], lw=2, color='b')  # Default color
        self.vacuum_line, = ax.plot([], [], [], lw=2, color='r')  # Vacuum color
        ax.set_xlim([-200, 200])
        ax.set_ylim([-200, 200])
        ax.set_zlim([0, 200])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('G-code Toolpath Simulation')

        def init():
            self.line.set_data([], [])
            self.line.set_3d_properties([])
            self.vacuum_line.set_data([], [])
            self.vacuum_line.set_3d_properties([])
            return self.line, self.vacuum_line

        # Initialize the plot without starting the animation
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
        coordinates = self.parse_gcode(self.gcode)
        self.plot_toolpath_animation(coordinates, interval=50)

    def plot_vacuum_toolpath(self):
        """Plot the vacuum toolpath from the G-code."""
        vacuum_start_line, vacuum_end_line = self.find_vacuum_gcode_lines()
        if vacuum_start_line is not None and vacuum_end_line is not None:
            vacuum_gcode = self.gcode[vacuum_start_line:vacuum_end_line + 1]
            coordinates = self.parse_gcode(vacuum_gcode)
            self.plot_toolpath_animation(coordinates, interval=50)
        else:
            print("No vacuum injection G-code found.")
