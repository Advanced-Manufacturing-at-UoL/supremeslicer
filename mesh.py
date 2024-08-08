import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
import re
import time
import yaml
from scipy.spatial import Delaunay

class SimulationProcessor:
    def __init__(self, filename):
        """Initialize class"""
        self.config_file = 'configs/simulation.yaml'
        self.filename = filename
        self.config = self.load_config()
        self.gcode = self.read_gcode()
        self.animating = False
        self.current_frame = 0
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

    def update_plot(self, num):
        """Update the plot with each new coordinate."""
        if not self.animating:  # Avoid updating if not animating
            return

        # Clear existing mesh
        if hasattr(self, 'mesh') and self.mesh:
            self.mesh.remove()
            self.mesh = None

        if self.is_mesh_displayed:  # Display mesh when paused
            x_vals, y_vals, z_vals = zip(*self.coords_np[:num])
            
            # Create a Delaunay triangulation
            points = np.array(list(zip(x_vals, y_vals)))
            tri = Delaunay(points)
            
            self.mesh = self.ax.plot_trisurf(x_vals, y_vals, z_vals, triangles=tri.simplices, color='r', alpha=0.5)  # Red color mesh
        else:
            # Reset display logic (not needed for mesh display)
            pass

        if self.show_travel:
            travel_lines = self.travel_coords_np[:num]
            if len(travel_lines):
                x_vals, y_vals, z_vals = zip(*travel_lines)
                if hasattr(self, 'travel_line') and self.travel_line:
                    self.travel_line.set_data(x_vals, y_vals)
                    self.travel_line.set_3d_properties(z_vals)
                else:
                    self.travel_line, = self.ax.plot(x_vals, y_vals, z_vals, color='g', lw=0.5)

        if self.slider.val != num:
            self.slider.set_val(num)

        self.fig.canvas.draw_idle()

    def pause_animation(self, event):
        """Pause the animation and display the mesh."""
        if self.animating:
            self.animating = False
            if hasattr(self, 'ani'):
                self.ani.event_source.stop()
            self.is_mesh_displayed = True  # Show mesh when paused
            self.update_plot(self.current_frame)  # Update plot to show mesh

    def play_animation(self, event):
        """Start or resume the animation from the current slider value."""
        if not self.animating:
            self.is_mesh_displayed = False  # Switch back to line display when playing
            self.animating = True
            try:
                self.current_frame = int(self.slider.val)
            except ValueError:
                self.current_frame = 0
            if hasattr(self, 'ani'):
                self.ani.event_source.stop()
            self.ani = animation.FuncAnimation(
                self.fig, self.update_plot, frames=range(self.current_frame, len(self.coords_np)),
                interval=self.interval, blit=False, repeat=False
            )
            self.fig.canvas.draw_idle()
        else:
            self.ani.event_source.start()

    def update_slider(self, val):
        """Update the plot based on the slider value."""
        if not self.animating: # Allow slider updates when paused
            current_time = time.time()
            if current_time - int(self.last_slider_update) > self.slider_update_interval:
                self.last_slider_update = current_time
                try:
                    frame = int(val)
                except ValueError:
                    frame = 0
                self.update_plot(frame)
                self.fig.canvas.draw_idle()

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
        common_e_coords_np = np.array([[x, y, z] for _, x, y, z, _ in e_coords_list])
        travel_coords = np.array([[x, y, z] for _, x, y, z, _ in travel_coords_list])
        coords = np.array([[x, y, z] for _, x, y, z, _, _ in coordinates])

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('3D Toolpath Animation')

        self.ax.set_xlim([np.min(coords[:, 0]), np.max(coords[:, 0])])
        self.ax.set_ylim([np.min(coords[:, 1]), np.max(coords[:, 1])])
        self.ax.set_zlim([np.min(coords[:, 2]), np.max(coords[:, 2])])

        self.e_coords_np = common_e_coords_np
        self.travel_coords_np = travel_coords
        self.coords_np = coords
        self.interval = interval

        # Initialize animation and controls
        self.ani = animation.FuncAnimation(
            self.fig, self.update_plot, frames=range(len(self.coords_np)),
            interval=interval, blit=False, repeat=False
        )

        # Add buttons and slider
        pause_ax = plt.axes([0.7, 0.02, 0.1, 0.075])
        play_ax = plt.axes([0.81, 0.02, 0.1, 0.075])
        forward_ax = plt.axes([0.59, 0.02, 0.1, 0.075])
        back_ax = plt.axes([0.48, 0.02, 0.1, 0.075])
        slider_ax = plt.axes([0.2, 0.15, 0.65, 0.03])

        self.slider = Slider(slider_ax, 'Frame', 0, len(self.coords_np)-1, valinit=0, valfmt='%d')
        self.slider.on_changed(self.update_slider)

        self.pause_button = Button(pause_ax, 'Pause')
        self.pause_button.on_clicked(self.pause_animation)

        self.play_button = Button(play_ax, 'Play')
        self.play_button.on_clicked(self.play_animation)

        self.forward_button = Button(forward_ax, '>>')
        self.forward_button.on_clicked(self.forward_frame)

        self.backward_button = Button(back_ax, '<<')
        self.backward_button.on_clicked(self.backward_frame)

        plt.show()
        self.fig.canvas.draw()

    def process_simulation(self, interval=100):
        """Process the G-code and generate the animation."""
        e_coords_list, travel_coords_list, coordinates = self.parse_gcode(self.gcode)
        self.plot_toolpath_animation(e_coords_list, travel_coords_list, coordinates, interval)

# Example usage
# sim_processor = SimulationProcessor("path_to_your_gcode_file.gcode")
# sim_processor.process_simulation(interval=100)

# Example usage
sim_processor = SimulationProcessor(r'output\benchy.gcode')
sim_processor.process_simulation(interval=100)