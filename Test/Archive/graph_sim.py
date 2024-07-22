import matplotlib.pyplot as plt

def parse_gcode(gcode):
    """Parse G-code and return a list of (x, y, z) coordinates and commands."""
    coordinates = []
    x, y, z = 0.0, 0.0, 0.0  # Starting point
    command = None
    
    for line in gcode.splitlines():
        line = line.strip()
        if line == "" or line.startswith(';'):  # Skip empty lines and comments
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
    
    return coordinates

def plot_toolpath(coordinates):
    """Plot the toolpath given a list of (command, x, y, z) coordinates."""
    if not coordinates:
        print("No coordinates to plot.")
        return
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    x_coords = []
    y_coords = []
    z_coords = []
    
    for command, x, y, z in coordinates:
        x_coords.append(x)
        y_coords.append(y)
        z_coords.append(z)
        
        if command == 'G0':  # Rapid movement (move without cutting)
            color = 'r'
        elif command == 'G1':  # Linear movement (cutting)
            color = 'b'
        else:
            color = 'k'  # Other movements

        ax.plot(x_coords, y_coords, z_coords, color=color)
        x_coords, y_coords, z_coords = [x], [y], [z]  # Start a new segment
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('G-code Toolpath Simulation')
    plt.show()

# Sample G-code
gcode = """
G0 X0 Y0 Z0
G1 X10 Y0 Z0
G1 X10 Y10 Z0
G1 X0 Y10 Z0
G1 X0 Y0 Z0
G0 X5 Y5 Z5
G1 X15 Y5 Z5
"""

coordinates = parse_gcode(gcode)
plot_toolpath(coordinates)
