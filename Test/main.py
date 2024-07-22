import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation

class GCodeProcessor:
    def __init__(self, filename):
        self.filename = filename
        self.gcode = self.read_gcode()

    def read_gcode(self):
        """Read G-code from a file."""
        with open(self.filename, 'r') as f:
            return f.readlines()

    def find_vacuum_gcode(self):
        """Extract vacuum injection G-code from the file."""
        start_comment = "; VacuumPnP TOOL G CODE INJECTION START"
        end_comment = "; VacuumPnP TOOL G CODE INJECTION END"

        specific_gcode = []
        block_found = False

        for l_no, line in enumerate(self.gcode):
            if start_comment in line:
                print(f"Found start comment in line {l_no}")
                block_found = True
            if block_found:
                specific_gcode.append(line)
                if end_comment in line:
                    print(f"Found end comment in line {l_no}")
                    break

        return specific_gcode if block_found else None

    def parse_gcode(self, gcode):
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
                    try:
                        x = float(part[1:])
                    except ValueError:
                        print(f"Warning: Skipping invalid X value: {part[1:]}")
                        x = 0.0  # Default value in case of error
                elif part.startswith('Y'):
                    try:
                        y = float(part[1:])
                    except ValueError:
                        print(f"Warning: Skipping invalid Y value: {part[1:]}")
                        y = 0.0  # Default value in case of error
                elif part.startswith('Z'):
                    try:
                        z = float(part[1:])
                    except ValueError:
                        print(f"Warning: Skipping invalid Z value: {part[1:]}")
                        z = 0.0  # Default value in case of error
            
            if command is not None:
                coordinates.append((command, x, y, z))
        
        interpolated_coords = []
        for i in range(len(coordinates) - 1):
            cmd1, x1, y1, z1 = coordinates[i]
            cmd2, x2, y2, z2 = coordinates[i + 1]
            
            if cmd1.startswith('G0') and cmd2.startswith('G1'):
                num_steps = 50
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

    def update_plot(self, num, coords, line, ax):
        """Update the plot with each new coordinate."""
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('G-code Toolpath Simulation')

        ax.set_xlim([-200, 200])
        ax.set_ylim([-200, 200])
        ax.set_zlim([0, 200])

        line, = ax.plot(coords[:num, 0], coords[:num, 1], coords[:num, 2], lw=2)
        return line,

    def plot_toolpath_animation(self, coordinates, filename, interval):
        """Animate the toolpath given a list of (command, x, y, z) coordinates and save to a file."""
        if not coordinates:
            print("No coordinates to animate.")
            return

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        coords_np = np.array([[x, y, z] for _, x, y, z in coordinates])
        line, = ax.plot([], [], [], lw=2)

        ani = animation.FuncAnimation(
            fig, self.update_plot, len(coords_np), fargs=(coords_np, line, ax),
            interval=interval, blit=False, repeat=False
        )

        # Save the animation as a GIF
        writer = animation.PillowWriter(fps=24)  # You can adjust fps
        ani.save(filename, writer=writer, dpi=100)
        print(f"Animation saved to {filename}")

    def plot_original_toolpath(self):
        """Plot the original toolpath from the full G-code."""
        coordinates = self.parse_gcode(self.gcode)
        self.plot_toolpath_animation(coordinates, 'toolpath_original.gif', interval=0.01)

    def plot_vacuum_toolpath(self):
        """Plot the vacuum toolpath from the G-code."""
        vacuum_gcode = self.find_vacuum_gcode()
        if vacuum_gcode:
            coordinates = self.parse_gcode(vacuum_gcode)
            self.plot_toolpath_animation(coordinates, 'toolpath_vacuum.gif', interval=0.01)
        else:
            print("No vacuum injection G-code found.")

if __name__ == "__main__":
    filename = r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\supremeslicer\output\injected_box.gcode'
    gcode_processor = GCodeProcessor(filename)
    
    try:
        print("1. Plot Original Toolpath")
        print("2. Plot Vacuum Toolpath")
        user_in = int(input("Generate original or toolspecific toolpath?"))

        if user_in == 1:
            gcode_processor.plot_original_toolpath()
            print("Completed toolpath")
        elif user_in == 2:
            gcode_processor.plot_vacuum_toolpath()
            print("Completed toolpath")
    except Exception as e:
        print(f"Error in simulation process: {e}")
