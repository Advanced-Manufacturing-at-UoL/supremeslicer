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

    def read_gcode(self):
        """Read G-code from a file."""
        with open(self.filename, 'r') as f:
            return f.readlines()

    def find_vacuum_gcode(self):
        """Extract vacuum injection G-code from the file."""
        start_comment = "; VacuumPnP TOOL G CODE INJECTION START"
        end_comment = "; VacuumPnP TOOL G CODE INJECTION END"

        specific_gcode = []
        block_found = False

        for l_no, line in enumerate(self.gcode):
            if start_comment in line:
                block_found = True
            if block_found:
                specific_gcode.append(line)
                if end_comment in line:
                    break

        return specific_gcode if block_found else None

    def parse_gcode(self, gcode):
        """Parse G-code and return a list of (command, x, y, z) coordinates."""
        coordinates = []
        x, y, z = 0.0, 0.0, 0.0
        
        for line in gcode:
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
                coordinates.append((command, x, y, z))
        
        interpolated_coords = []
        for i in range(len(coordinates) - 1):
            cmd1, x1, y1, z1 = coordinates[i]
            cmd2, x2, y2, z2 = coordinates[i + 1]
            
            if cmd1.startswith('G0') and cmd2.startswith('G1'):
                num_steps = 10  # Adjust number of interpolation steps
                xs = np.linspace(x1, x2, num_steps)
                ys = np.linspace(y1, y2, num_steps)
                zs = np.linspace(z1, z2, num_steps)
                
                interpolated_coords.extend(('G1', xs[j], ys[j], zs[j]) for j in range(num_steps))
            else:
                interpolated_coords.append((cmd1, x1, y1, z1))
        
        if coordinates:
            interpolated_coords.append(coordinates[-1])
        
        return interpolated_coords

    def update_plot(self, num, coords, line):
        """Update the plot with each new coordinate."""
        line.set_data(coords[:num, 0], coords[:num, 1])
        line.set_3d_properties(coords[:num, 2])
        return line,

    def plot_toolpath_animation(self, coordinates, interval):
        """Animate the toolpath given a list of (command, x, y, z) coordinates."""
        if not coordinates:
            print("No coordinates to animate.")
            return

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        coords_np = np.array([[x, y, z] for _, x, y, z in coordinates])
        num_frames = len(coords_np)

        # Plot only once
        line, = ax.plot([], [], [], lw=2)
        ax.set_xlim([-200, 200])
        ax.set_ylim([-200, 200])
        ax.set_zlim([0, 200])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('G-code Toolpath Simulation')

        def init():
            line.set_data([], [])
            line.set_3d_properties([])
            return line,

        ani = animation.FuncAnimation(
            fig, self.update_plot, num_frames, fargs=(coords_np, line),
            init_func=init, interval=interval, blit=False, repeat=False
        )

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
        slider = Slider(ax_slider, 'Frame', 0, num_frames - 1, valinit=0, valstep=1)

        def play(event):
            ani.event_source.start()

        def pause(event):
            ani.event_source.stop()

        def forward(event):
            slider.set_val(min(slider.val + 1, num_frames - 1))

        def backward(event):
            slider.set_val(max(slider.val - 1, 0))

        def update_slider(val):
            frame = int(val)
            line.set_data(coords_np[:frame, 0], coords_np[:frame, 1])
            line.set_3d_properties(coords_np[:frame, 2])
            fig.canvas.draw_idle()

        btn_play.on_clicked(play)
        btn_pause.on_clicked(pause)
        btn_forward.on_clicked(forward)
        btn_backward.on_clicked(backward)
        slider.on_changed(update_slider)

        plt.show()

    def plot_original_toolpath(self):
        """Plot the original toolpath from the full G-code."""
        coordinates = self.parse_gcode(self.gcode)
        self.plot_toolpath_animation(coordinates, interval=50)

    def plot_vacuum_toolpath(self):
        """Plot the vacuum toolpath from the G-code."""
        vacuum_gcode = self.find_vacuum_gcode()
        if vacuum_gcode:
            coordinates = self.parse_gcode(vacuum_gcode)
            self.plot_toolpath_animation(coordinates, interval=50)
        else:
            print("No vacuum injection G-code found.")
