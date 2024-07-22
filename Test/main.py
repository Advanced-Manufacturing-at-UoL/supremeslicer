import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation

def parse_gcode(gcode):
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
                x = float(part[1:])
            elif part.startswith('Y'):
                y = float(part[1:])
            elif part.startswith('Z'):
                z = float(part[1:])
        
        # Only append coordinates if a command is present
        if command is not None:
            coordinates.append((command, x, y, z))
    
    interpolated_coords = []
    for i in range(len(coordinates) - 1):
        cmd1, x1, y1, z1 = coordinates[i]
        cmd2, x2, y2, z2 = coordinates[i + 1]
        
        if cmd1.startswith('G0') and cmd2.startswith('G1'):
            num_steps = 10
            xs = np.linspace(x1, x2, num_steps)
            ys = np.linspace(y1, y2, num_steps)
            zs = np.linspace(z1, z2, num_steps)
            
            for j in range(num_steps):
                interpolated_coords.append(('G1', xs[j], ys[j], zs[j]))
        else:
            interpolated_coords.append((cmd1, x1, y1, z1))
    
    if coordinates:
        interpolated_coords.append(coordinates[-1])
    
    return interpolated_coords

def update_plot(num, coords, line):
    """Update the plot with each new coordinate."""
    line.set_data(coords[:num, 0], coords[:num, 1])
    line.set_3d_properties(coords[:num, 2])
    return line,

def plot_toolpath_animation(coordinates, interval):
    """Animate the toolpath given a list of (command, x, y, z) coordinates."""
    if not coordinates:
        print("No coordinates to animate.")
        return
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('G-code Toolpath Simulation')

    ax.set_xlim([-200, 200])
    ax.set_ylim([-200, 200])
    ax.set_zlim([0, 200])

    coords_np = np.array([[x, y, z] for _, x, y, z in coordinates])
    line, = ax.plot([], [], [], lw=2)

    ani = animation.FuncAnimation(
        fig, update_plot, len(coords_np), fargs=(coords_np, line),
        interval=interval, blit=False, repeat=False
    )

    plt.show()

def read_gcode(filename):
    """Read G-code from a file."""
    with open(filename, 'r') as f:
        return f.readlines()

def find_vacuum_gcode(filename):
    """Extract vacuum injection G-code from the file."""
    start_comment = "; VacuumPnP TOOL G CODE INJECTION START"
    end_comment = "; VacuumPnP TOOL G CODE INJECTION END"

    specific_gcode = []
    block_found = False

    with open(filename, 'r') as f:
        for l_no, line in enumerate(f):
            if start_comment in line:
                print(f"Found start comment in line {l_no}")
                block_found = True
            if block_found:
                specific_gcode.append(line)
                if end_comment in line:
                    print(f"Found end comment in line {l_no}")
                    break

    return specific_gcode if block_found else None

if __name__ == "__main__":
    filename = r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\supremeslicer\output\injected_box.gcode'
    
    gcode = find_vacuum_gcode(filename)
    if gcode:
        coordinates = parse_gcode(gcode)
        plot_toolpath_animation(coordinates, interval=0.1)
    else:
        print("No vacuum injection G-code found.")
