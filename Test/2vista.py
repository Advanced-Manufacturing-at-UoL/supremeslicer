import pyvista as pv
import numpy as np
import re

class ToolpathAnimator:
    def __init__(self, gcode_file):
        self.gcode_file = gcode_file
        self.plot_data = None
        self.plotter = None

    def parse_gcode(self):
        """Parse the G-code file and extract X, Y, Z coordinates, layer info, and move types."""
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

    @staticmethod
    def create_toolpath_mesh(x, y, z, radius, resolution=10):
        points = np.column_stack((x, y, z))
        lines = []
        for i in range(len(points) - 1):
            lines.append([2, i, i+1])
        poly = pv.PolyData(points, lines=lines)
        return poly.tube(radius=radius, n_sides=resolution)

    def animate_toolpath(self):
        if self.plot_data is None:
            raise ValueError("Plot data is not initialized. Please run parse_gcode first.")
        
        self.plotter = pv.Plotter()
        self.plotter.set_background('white')
        
        categories = {
            ('polymer', 'travel'): {'color': 'pink', 'radius': 0.1},
            ('polymer', 'print'): {'color': 'red', 'radius': 0.3},
            ('ceramic', 'travel'): {'color': 'lightblue', 'radius': 0.1},
            ('ceramic', 'print'): {'color': 'blue', 'radius': 0.6}
        }
        
        layers = sorted(set(self.plot_data['layer']))

        # Open a movie file
        self.plotter.open_movie('toolpath_building.mp4', framerate=10)
        
        # Create a dictionary to hold meshes for each layer
        meshes_per_layer = {layer: [] for layer in layers}
        
        # Create meshes for each layer and store them
        for layer in layers:
            for (material, move_type), properties in categories.items():
                mask = [(s == material and t == move_type and l == layer) 
                        for s, t, l in zip(self.plot_data['system'], self.plot_data['type'], self.plot_data['layer'])]
                if any(mask):
                    x = np.array(self.plot_data['X'])[mask]
                    y = np.array(self.plot_data['Y'])[mask]
                    z = np.array(self.plot_data['Z'])[mask]
                    
                    if len(x) > 1:
                        mesh = self.create_toolpath_mesh(x, y, z, radius=properties['radius'])
                        meshes_per_layer[layer].append((mesh, properties['color']))

        # Initialize the plotter with empty content
        self.plotter.add_text('Layer 0', font_size=12, color='black')
        self.plotter.show_axes()
        self.plotter.show_grid()
        
        for step in range(len(layers)):
            # Clear only plot data, keep the axes
            self.plotter.clear_actors()
            
            # Add meshes up to the current layer
            for layer in layers[:step + 1]:
                for mesh, color in meshes_per_layer[layer]:
                    self.plotter.add_mesh(mesh, color=color)
            
            # Update the text to show the current layer
            self.plotter.add_text(f'Layer {layers[step]}', font_size=12, color='black')

            # Write the frame
            self.plotter.write_frame()
        
        # Close the movie file
        self.plotter.close()

# Usage example
animator = ToolpathAnimator(r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\supremeslicer\output\benchy.gcode')
animator.parse_gcode()
animator.animate_toolpath()
