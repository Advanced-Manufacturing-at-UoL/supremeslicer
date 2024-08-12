import pyvista as pv
import numpy as np
import re
import time

class ToolpathAnimator:
    """Toolpath Animation Class for PyVista approach"""
    def __init__(self, gcode_file):
        self.gcode_file = gcode_file
        self.plot_data = None
        self.plotter = None
        self.layers = None
        self.meshes_per_layer = None
        self.current_step = 0
        self.is_playing = False
        self.slider = None

    def parse_gcode(self):
        """Parse the G-code file and extract X, Y, Z coordinates, layer info, and move types."""
        print("Parsing Gcode")
        start_time = time.time()
        data = {
            'X': [],
            'Y': [],
            'Z': [],
            'layer': [],
            'system': [],
            'type': []
        }
        
        layer = 0
        current_z = 0.0
        material = 'polymer'  # Default material
        move_type = 'travel'  # Default move type

        # Open the GCode File
        with open(self.gcode_file, 'r') as file:
            gcode = file.readlines()

        for line in gcode:
            line = line.strip()

            # Detect new layer
            if line.startswith(';LAYER_CHANGE'):
                layer += 1
                continue
            
            # Extract Z height
            z_match = re.search(r'G[01].*Z([-+]?\d*\.\d+|\d+)', line)
            if z_match:
                current_z = float(z_match.group(1))
            
            # Extract X, Y coordinates
            x_match = re.search(r'X([-+]?\d*\.\d+|\d+)', line)
            y_match = re.search(r'Y([-+]?\d*\.\d+|\d+)', line)

            if x_match and y_match:
                data['X'].append(float(x_match.group(1)))
                data['Y'].append(float(y_match.group(1)))
                data['Z'].append(current_z)
                data['layer'].append(layer)
                data['system'].append(material)
                data['type'].append(move_type)
            
            # Identify move type
            if "E" in line:
                move_type = 'print'
            elif "G0" in line or "G1" in line:
                move_type = 'travel'

        self.plot_data = data
        end_time = time.time()
        print(f"Time taken to start animation {round((start_time-end_time),2)}\n")

    @staticmethod
    def create_toolpath_mesh(x, y, z, radius, resolution=10):
        """Create a tube mesh representing the toolpath."""
        points = np.column_stack((x, y, z))
        lines = [[2, i, i + 1] for i in range(len(points) - 1)]
        poly = pv.PolyData(points, lines=lines)
        return poly.tube(radius=radius, n_sides=resolution)

    def setup_plotter(self):
        """Setup the plotter with widgets for slider."""
        print("Setting up plotter\n")
        start_time = time.time()

        self.plotter = pv.Plotter()
        self.plotter.set_background('white')
        self.plotter.add_text('Layer 0', font_size=12, color='black')

        # Define colors and radii for different categories
        categories = {
            ('polymer', 'travel'): {'color': 'pink', 'radius': 0.1},
            ('polymer', 'print'): {'color': 'red', 'radius': 0.3},
            ('ceramic', 'travel'): {'color': 'lightblue', 'radius': 0.1},
            ('ceramic', 'print'): {'color': 'blue', 'radius': 0.6}
        }

        # Prepare a dictionary to store meshes for each layer
        self.meshes_per_layer = {layer: [] for layer in self.layers}

        # Generate and store meshes for each layer
        for layer in self.layers:
            for (material, move_type), properties in categories.items():
                mask = [(s == material and t == move_type and l == layer) 
                        for s, t, l in zip(self.plot_data['system'], self.plot_data['type'], self.plot_data['layer'])]
                if any(mask):
                    x = np.array(self.plot_data['X'])[mask]
                    y = np.array(self.plot_data['Y'])[mask]
                    z = np.array(self.plot_data['Z'])[mask]
                    if len(x) > 1:
                        mesh = self.create_toolpath_mesh(x, y, z, radius=properties['radius'])
                        self.meshes_per_layer[layer].append((mesh, properties['color']))

        # Add slider widget
        def slider_callback(value):
            self.current_step = int(value)
            self.update_plot()

        self.slider = self.plotter.add_slider_widget(
            slider_callback, 
            title='Layer', 
            rng=(0, len(self.layers)),
            value=0,
            pointa=(0.1, 0.05, 0),
            pointb=(0.9, 0.05, 0)
        )

        
        end_time = time.time()
        print(f"Time taken to setup animation: {round((start_time-end_time),2)}\n")

    def update_plot(self):
        """Update the plotter to show the current step."""
        self.plotter.clear_actors()  # Clear only the plot data, keeping the axes

        for layer in self.layers[:self.current_step + 1]:
            for mesh, color in self.meshes_per_layer[layer]:
                self.plotter.add_mesh(mesh, color=color)
        
        # Update the text to show the current layer
        self.plotter.add_text(f'Layer {self.layers[self.current_step -1]}', font_size=12, color='black')
        self.plotter.render()        
        self.plotter.show_axes_all()
        self.plotter.show_grid()
        self.plotter.show()

    def animate_toolpath(self):
        """Set up the plotter and display the interactive animation."""
        print("Animating toolpath")
        start_time = time.time()
        self.layers = sorted(set(self.plot_data['layer']))
        self.setup_plotter()
        # Main loop for play/pause control

        end_time = time.time()
        print(f"Time taken to automatically render animation {round((start_time-end_time),2)}\n")
        
        try:
            while True:
                if self.is_playing and self.current_step < len(self.layers) - 1:
                    self.current_step += 1
                    self.update_plot()
                    time.sleep(0.1)  # Adjust this delay as needed

        except KeyboardInterrupt:
            print("Keyboard interrupt detected, exitting program")
            pass
        
        finally:
            print("Exitting")
            pass