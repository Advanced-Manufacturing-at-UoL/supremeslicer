import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import re

class SimulationProcessor:
    def __init__(self, filename):
        """Initialize class"""
        self.filename = filename
        self.gcode = self.read_gcode()

    def read_gcode(self):
        """Read G-code from a file."""
        try:
            with open(self.filename, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            raise(f"Error: File {self.filename} not found.")

    def parse_gcode(self, gcode):
        """Parse G-code and return lists of extrusion coordinates."""
        e_coordinates = []

        x, y, z = 0.0, 0.0, 0.0
        coordinate_pattern = re.compile(r'(X[-\d.]+|Y[-\d.]+|Z[-\d.]+|E[-\d.]+)')

        for line in gcode:
            line = line.strip()
            if not line or line.startswith(';'):
                continue  # Ignore comments

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
                except ValueError:
                    print(f"Error parsing coordinate: {coord}")

            if contains_e:
                e_coordinates.append((x, y, z))

        return e_coordinates

    def generate_mesh(self, e_coordinates, grid_size=100):
        """Generate a mesh from the extrusion coordinates."""
        e_coordinates = np.array(e_coordinates)
        x = e_coordinates[:, 0]
        y = e_coordinates[:, 1]
        z = e_coordinates[:, 2]

        # Create a grid for the mesh
        xi = np.linspace(min(x), max(x), grid_size)
        yi = np.linspace(min(y), max(y), grid_size)
        xi, yi = np.meshgrid(xi, yi)

        # Interpolate the Z values on the grid
        zi = plt.mlab.griddata(x, y, z, xi, yi, interp='linear')

        return xi, yi, zi

    def plot_mesh(self, xi, yi, zi):
        """Plot the mesh in 3D."""
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(xi, yi, zi, cmap='viridis')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('3D Mesh from G-code')

        plt.show()

    def run(self):
        """Run the mesh generation and plotting."""
        e_coords = self.parse_gcode(self.gcode)
        xi, yi, zi = self.generate_mesh(e_coords)
        self.plot_mesh(xi, yi, zi)

# Example usage
processor = SimulationProcessor(r'output\benchy.gcode')
processor.run()
