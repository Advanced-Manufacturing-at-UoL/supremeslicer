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
            raise FileNotFoundError(f"Error: File {self.filename} not found.")

    def parse_gcode(self, gcode):
        """Parse G-code and return a list of coordinates."""
        coordinates = []

        x, y, z = 0.0, 0.0, 0.0
        command_pattern = re.compile(r'([G]\d+)')
        coordinate_pattern = re.compile(r'(X[-\d.]+|Y[-\d.]+|Z[-\d.]+)')

        for line in gcode:
            line = line.strip()
            if not line or line.startswith(';'):
                continue  # Ignore comments

            command_match = command_pattern.search(line)
            command = command_match.group(1) if command_match else None

            coords = coordinate_pattern.findall(line)

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

            if command and (command == 'G0' or command == 'G1'):
                coordinates.append((x, y, z))

        return np.array(coordinates)

    def plot_static_mesh(self, coordinates):
        """Plot a static 3D mesh."""
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Static 3D Mesh from G-code')

        x_vals, y_vals, z_vals = coordinates[:, 0], coordinates[:, 1], coordinates[:, 2]

        # Create a Delaunay triangulation
        if len(x_vals) > 2:
            from scipy.spatial import Delaunay
            points = np.array(list(zip(x_vals, y_vals)))
            tri = Delaunay(points)
            mesh = ax.plot_trisurf(x_vals, y_vals, z_vals, triangles=tri.simplices, color='red', alpha=0.5)
        else:
            ax.scatter(x_vals, y_vals, z_vals, c='red', marker='o')

        plt.show()

    def process_simulation(self):
        """Process the G-code and generate a static mesh."""
        coordinates = self.parse_gcode(self.gcode)
        self.plot_static_mesh(coordinates)

# Example usage
sim_processor = SimulationProcessor(r'output\benchy.gcode')
sim_processor.process_simulation()
