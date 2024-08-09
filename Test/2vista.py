import pyvista as pv
import numpy as np
import re
import imageio
import os

def parse_gcode(gcode):
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

    return data

def create_toolpath_mesh(x, y, z, radius, resolution=10):
    points = np.column_stack((x, y, z))
    lines = []
    for i in range(len(points) - 1):
        lines.append([2, i, i+1])
    poly = pv.PolyData(points, lines=lines)
    return poly.tube(radius=radius, n_sides=resolution)

def create_gif(plot_data, gif_filename='toolpath_animation.gif'):
    plotter = pv.Plotter(off_screen=True)
    plotter.set_background('white')
    
    categories = {
        ('polymer', 'travel'): {'color': 'pink', 'radius': 0.1},
        ('polymer', 'print'): {'color': 'red', 'radius': 0.3},
        ('ceramic', 'travel'): {'color': 'lightblue', 'radius': 0.1},
        ('ceramic', 'print'): {'color': 'blue', 'radius': 0.6}
    }
    
    layers = sorted(set(plot_data['layer']))
    
    # Directory to save frames
    temp_dir = 'frames'
    os.makedirs(temp_dir, exist_ok=True)
    
    frame_filenames = []
    
    for step, layer in enumerate(layers):
        plotter.clear()  # Clear previous layer's plot
        
        for (material, move_type), properties in categories.items():
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
        
        plotter.add_text(f'Layer {layer}', font_size=12, color='black')
        plotter.show_axes()
        plotter.show_grid()
        
        # Save the current frame
        frame_filename = os.path.join(temp_dir, f'frame_{step:03d}.png')
        plotter.screenshot(frame_filename)
        frame_filenames.append(frame_filename)
    
    # Create GIF
    with imageio.get_writer(gif_filename, mode='I', duration=0.5) as writer:
        for filename in frame_filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
    
    # Clean up
    for filename in frame_filenames:
        os.remove(filename)
    os.rmdir(temp_dir)

# Usage example
with open(r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\supremeslicer\output\benchy.gcode', 'r') as file:
    gcode_lines = file.readlines()

parsed_data = parse_gcode(gcode_lines)
create_gif(parsed_data, 'toolpath_animation.gif')
