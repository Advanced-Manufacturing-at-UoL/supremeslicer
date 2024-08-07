import pyvista as pv
import numpy as np
from GcodeParser import GCodeParser

def create_toolpath_mesh(x, y, z, radius, resolution=10):
    points = np.column_stack((x, y, z))
    lines = []
    for i in range(len(points) - 1):
        lines.append([2, i, i+1])
    poly = pv.PolyData(points, lines=lines)
    return poly.tube(radius=radius, n_sides=resolution)

def visualize_toolpath(parser):
    plot_data = parser.get_plot_data()
    
    plotter = pv.Plotter()
    plotter.set_background('white')
    
    categories = {
        ('polymer', 'travel'): {'color': 'pink', 'radius': 0.1},
        ('polymer', 'print'): {'color': 'red', 'radius': 0.3},
        ('ceramic', 'travel'): {'color': 'lightblue', 'radius': 0.1},
        ('ceramic', 'print'): {'color': 'blue', 'radius': 0.6}
    }
    
    for (material, move_type), properties in categories.items():
        for layer in set(plot_data['layer']):
            mask = [(s == material and t == move_type and l == layer) 
                    for s, t, l in zip(plot_data['system'], plot_data['type'], plot_data['layer'])]
            if any(mask):
                x = np.array(plot_data['X'])[mask]
                y = np.array(plot_data['Y'])[mask]
                z = np.array(plot_data['Z'])[mask]
                
                if len(x) > 1:
                    mesh = create_toolpath_mesh(x, y, z, radius=properties['radius'])
                    plotter.add_mesh(mesh, color=properties['color'], 
                                     label=f"{material.capitalize()} {move_type} (Layer {layer})")
    
    plotter.add_legend()
    plotter.show_axes()
    plotter.show_grid()
    
    plotter.show(title="3D Toolpath Visualization")

# Usage
parser = GCodeParser()
# parser.parse_file('mini.tap')
parser.parse_file(r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\supremeslicer\output\benchy.gcode')
visualize_toolpath(parser)

print("\nLayer Z values:")
for layer, z_value in sorted(parser.layer_z_values.items()):
    print(f"Layer {layer}: Z = {z_value}")

# Print summary and debug info
parser.print_move_summary()
print("\nDebug log (last 20 lines):")
for log in parser.debug_log[-20:]:
    print(log)