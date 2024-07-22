# Test File to generate G code


# Import Libraries for generating animation and graph
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation

"""Parse G-code and return a list of (x, y, z) coordinates and commands."""
def parse_gcode(gcode):
    coordinates = []
    x, y, z = 0.0, 0.0, 0.0  # Home Position
    command = None
    
    for line in gcode:
        line = line.strip()
        if line == "" or line.startswith(';'):
            continue

        parts = line.split()
        for part in parts:
            if part.startswith('G'):
                command = part
            elif part.startswith('X'):
                x = float(part[1:])
            elif part.startswith('Y'):
                y = float(part[1:])
            elif part.startswith('Z'):
                z = float(part[1:])
        
        coordinates.append((command, x, y, z))
    
    # Generate intermediate points for smooth animation
    interpolated_coords = []
    for i in range(len(coordinates) - 1):
        cmd1, x1, y1, z1 = coordinates[i]
        cmd2, x2, y2, z2 = coordinates[i + 1]
        
        if cmd1.startswith('G0') and cmd2.startswith('G1'):
            # Generate intermediate points between G0 and G1
            num_steps = 10  # Number of steps to interpolate
            xs = np.linspace(x1, x2, num_steps)
            ys = np.linspace(y1, y2, num_steps)
            zs = np.linspace(z1, z2, num_steps)
            
            for j in range(num_steps):
                interpolated_coords.append(('G1', xs[j], ys[j], zs[j]))
        else:
            interpolated_coords.append((cmd1, x1, y1, z1))
    
    interpolated_coords.append(coordinates[-1])  # Add the last coordinate
    
    return interpolated_coords

"""Function to update the plot with each new coordinate"""
def update_plot(num, coordinates, line):
    line.set_data(coordinates[:num, 0], coordinates[:num, 1])
    line.set_3d_properties(coordinates[:num, 2])
    return line

"""Animate the toolpath given a list of (command, x, y, z) coordinates."""
def plot_toolpath_animation(coordinates, interval):
    if not coordinates:
        print("No coordinates to animate.")
        return
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('G-code Toolpath Simulation')

    # Increase the size of axes
    ax.set_xlim([-200, 200])
    ax.set_ylim([-200, 200])
    ax.set_zlim([0, 200])

    coordinates_np = np.array([[x, y, z] for command, x, y, z in coordinates])

    line, = ax.plot([], [], [], lw=2)

    ani = animation.FuncAnimation(fig, update_plot, len(coordinates_np), fargs=(coordinates_np, line),
                                  interval=interval, blit=False, repeat=False)

    plt.show()

"""Function to read gcode from file"""
def read_gcode(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return lines


"""Function to find just the vacuum injection"""
def find_vacuum_gcode(filename):
    start_comment = "; VacuumPnP TOOL G CODE INJECTION START"
    end_comment = "; VacuumPnP TOOL G CODE INJECTION END"

    specific_gcode = []
    block_found = False

    with open(filename, 'r') as f:
        lines = f.readlines()

    for l_no, line in enumerate(lines):
        if start_comment in line:
            print(f"Found start comment in line number {l_no}")
            block_found = True
            specific_gcode.append(line)
        elif block_found:
            specific_gcode.append(line)
            if end_comment in line:
                print(f"Found end comment in line number {l_no}")
                break

    if block_found:
        return specific_gcode
    else:
        return None

if __name__ == "__main__":
    filename = r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\supremeslicer\output\box.gcode'
    
    # gcode = read_gcode(filename)
    gcode = find_vacuum_gcode(filename)
    coordinates = parse_gcode(gcode)
    plot_toolpath_animation(coordinates, interval = 0.1)
