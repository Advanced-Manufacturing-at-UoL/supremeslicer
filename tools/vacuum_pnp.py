import os
import math
from lib.utils import Utils

class VacuumPnP:
    """Class for handling functions for the VacuumPnP tool"""
    def __init__(self, filename, config_file):
        self.filename = filename
        self.config_file = config_file
        self.gcode_content = None
        self.injected_gcode = None

        # Load configuration from YAML file
        self.load_config()

    def load_config(self):
        """Loads the parameters from the YAML configuration file."""
        try:
            config = Utils.read_yaml(self.config_file)
            self.zHop_mm = config.get('zHop_mm', 100.0)
            self.startX = config.get('startX', 100.0)
            self.startY = config.get('startY', 100.0)
            self.startZ = config.get('startZ', 100.0)
            self.suctionState = config.get('suctionState', 0)
            self.endX = config.get('endX', 150.0)
            self.endY = config.get('endY', 150.0)
            self.endZ = config.get('endZ', 150.0)

            print("Configuration loaded successfully.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: Configuration file not found: {self.config_file}")
        except Exception as e:
            raise Exception(f"Error: {e}")

    def read_gcode(self):
        """Reads the G-code file and stores its content."""
        try:
            with open(self.filename, 'r') as file:
                self.gcode_content = file.read()
                print("\nG-code file read successfully.")
        except FileNotFoundError:
            print(f"Error: G-code file not found: {self.filename}")
        except IOError as e:
            print(f"Error reading G-code file: {e}")

    def generate_gcode(self):
        """Generates the G-code injection based on the parameters from the YAML configuration."""
        self.injected_gcode = f""";-----------------------------------------------
; VacuumPnP TOOL G CODE INJECTION START
; VIBRATE FIRST
G90 ; Ensure we're using absolute positioning rather than relative
G0 Z{self.zHop_mm:.2f} ; Move to zHop position for clearance
TOOL_PICKUP T=3 ; Pickup the Gripper tool
GRIPPER_CLOSE CLOSURE={self.gripperOpenAngle} ; Open Gripper before using tool
G0 X{self.startX:.2f} Y{self.startY:.2f} ; Move to where you want to suck in X,Y
G0 Z{self.startZ:.2f} ; Lower Z to start position
GRIPPER_CLOSE CLOSURE={self.gripperCloseAngle} ; Close Gripper around part
GRIPPER_BUZZ CYCLES=100 ; Vibrate the part to separate it from the bed
GRIPPER_CLOSE CLOSURE = {self.gripperOpenAngle} ; Open Gripper to release grip
G0 Z{self.zHop_mm:.2f} ; Move to zHop position for clearance
TOOL_PICKUP T=2 ; Pickup the vacuum tool
G0 X{self.startX:.2f} Y{self.startY:.2f} ; Move to where you want to suck in X,Y
G0 Z{self.startZ:.2f} ; Lower Z to start position
SET_PIN PIN=VACUUM VALUE={self.suctionState} ; Execute suction state
G0 Z{self.zHop_mm:.2f} ; Make zHop Clearance so things don't get knocked over
G0 X{self.endX:.2f} Y{self.endY:.2f} ; Move to endPosition for what we're dropping object to
G0 Z{self.endZ:.2f} ; Move to height of drop
SET_PIN PIN=VACUUM VALUE={0.00} ; Stop Suction state
G0 Z{self.zHop_mm:.2f} ; Move to zHop position for clearance
TOOL_PICKUP T=0 ; Pickup the Extruder tool again, but this only works for single extruder
G91 ; Set back to relative positioning 
; VacuumPnP TOOL G CODE INJECTION END
;-----------------------------------------------
"""
        print("G-code injection generated.")

    def inject_gcode_at_height(self, target_height, output_path):
        """Injects the generated G-code at the specified height into a new file."""
        layers = self._height_parser()

        if not layers:
            print("Error: No layer changes found in the G-code file.")
            return

        if not self.gcode_content:
            print("Error: G-code content is empty. Please read the G-code file first.")
            return

        if not self.injected_gcode:
            print("Error: No G-code injection generated. Please generate G-code first.")
            return

        closest_height = min(layers.keys(), key=lambda x: abs(x - target_height))
        injection_point = layers[closest_height]
        print(f"Injecting at closest height: {closest_height} (Layer Change at line {injection_point})")

        with open(self.filename, 'r') as f:
            lines = f.readlines()

        custom_gcode_lines = self.injected_gcode.splitlines()
        lines.insert(injection_point + 1, '\n'.join(custom_gcode_lines) + '\n')

        # Define the output path
        output_file = Utils.get_resource_path(os.path.join(output_path, os.path.basename(self.filename)))

        with open(output_file, 'w') as f:
            f.writelines(lines)

        print(f"G-code injected and saved to {output_file}\n")
    
    def inject_gcode_given_coordinates(self, output_path):
        """Injects the generated G-code at the closest line based on user-provided coordinates into a new file."""
        if not self.gcode_content:
            print("Error: G-code content is empty. Please read the G-code file first.")
            return

        if not self.injected_gcode:
            print("Error: No G-code injection generated. Please generate G-code first.")
            return

        # Coordinates to inject the G-code
        target_x = (self.startX)
        target_y = (self.startY)
        target_z = (self.startZ)

        print("Target values selected")
        print(f"G1 X{target_x:.3f} Y{target_y:.3f} Z{target_z:.3f}")

        # Find the closest Z-coordinate in the file
        closest_z, lines_at_z = self._find_lines_at_closest_z(target_z-1)

        if not lines_at_z:
            print(f"No coordinates found at or near Z={target_z:.2f}")
            return

        print(f"Found Z={closest_z:.3f} in the G-code. Searching for closest (X, Y) at that height...")

        # Find the closest (X, Y) at that Z height
        injection_point = self._find_closest_xy_in_lines(lines_at_z[0], target_x, target_y)
        print(f"The Injection point is: {injection_point}")

        if injection_point == -1:
            print(f"No matching X, Y found near Z={closest_z:.3f}. Unable to inject the G-code.")
            return

        print(f"Injecting at line: {injection_point[0]}")

        # Inject the G-code at the closest point
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        custom_gcode_lines = self.injected_gcode.splitlines()
        lines.insert(injection_point[0] + 1, '\n'.join(custom_gcode_lines) + '\n')

        # Define the output path
        output_file = Utils.get_resource_path(os.path.join(output_path, os.path.basename(self.filename)))

        with open(output_file, 'w') as f:
            f.writelines(lines)

        print(f"G-code injected and saved to {output_file}\n")

    def inject_gcode_final_layer(self, output_path):
        """Injects the generated G-code at the closest line based on user-provided coordinates into a new file."""
        if not self.gcode_content:
            print("Error: G-code content is empty. Please read the G-code file first.")
            return

        if not self.injected_gcode:
            print("Error: No G-code injection generated. Please generate G-code first.")
            return

        # Coordinates to inject the G-code
        target_x = (self.startX)
        target_y = (self.startY)
        target_z = (self.startZ)

        print("Target values selected")
        print(f"G1 X{target_x:.3f} Y{target_y:.3f} Z{target_z:.3f}")

        print(f"Injecting target values: {target_x, target_y, target_z}")

        # Inject the G-code at the closest point
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        # Find the line containing the 'END_PRINT' marker
        try:
            end_print_index = next(i for i, line in enumerate(lines) if 'END_PRINT' in line)
        except StopIteration:
            print("Error: 'END_PRINT' marker not found in the G-code file.")
            return

        # Split the generated G-code into lines and insert them before 'END_PRINT'
        custom_gcode_lines = self.injected_gcode.splitlines()
        lines[end_print_index:end_print_index] = [line + '\n' for line in custom_gcode_lines]

        # Define the output file path
        output_file = Utils.get_resource_path(os.path.join(output_path, os.path.basename(self.filename)))

        # Write the modified lines back to the file
        with open(output_file, 'w') as f:
            f.writelines(lines)

        print(f"G-code injected and saved to {output_file}\n")

    def _find_lines_at_closest_z(self, target_z):
        """Finds the closest Z height and returns the lines that match this Z height."""
        closest_z = None
        min_z_diff = 0.4
        lines_at_z = []

        with open(self.filename, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith('G0') or line.startswith('G1'):
                coords = self._parse_gcode_line(line)
                if coords:
                    x, y, z = coords
                    if z is not None:
                        z_diff = abs(z - target_z)
                        if z_diff < min_z_diff:
                            min_z_diff = z_diff
                            closest_z = z
                            lines_at_z = []
                        if z == closest_z:
                            lines_at_z.append((i))
        
        print(f"The closest z found was: {closest_z}")
        print(f"The lines at this z position was: {lines_at_z}\n")

        return closest_z, lines_at_z


    def _find_closest_xy_in_lines(self, start_index, target_x=None, target_y=None):
        """Search the G-code file from a specific index onward, looking for the closest (X, Y) coordinates."""
        closest_distance = float('inf')
        closest_index = -1
        found_coordinates = None

        # Open the G-code file and read the lines
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        # Start searching from the provided start_index
        for i in range(int(start_index), len(lines)):
            line = lines[i].strip()
            if line.startswith('G0') or line.startswith('G1'):
                coords = self._parse_gcode_line(line)
                if coords:
                    x, y, z = coords
                    if x is not None and y is not None and target_x is not None and target_y is not None:
                        distance = math.sqrt((x - target_x) ** 2 + (y - target_y) ** 2)
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_index = i
                            found_coordinates = (x, y)

        return closest_index, closest_distance, found_coordinates

    def _parse_gcode_line(self, line):
        """Parses a G-code line to extract X, Y, Z coordinates."""
        x = y = z = None
        parts = line.split()
        for part in parts:
            if part.startswith('X'):
                x = float(part[1:])
            elif part.startswith('Y'):
                y = float(part[1:])
            elif part.startswith('Z'):
                z = float(part[1:])
        if x is not None or y is not None or z is not None:
            return (x, y, z)

    def _height_parser(self):
        """Parses the G-code file to find layer change heights and their corresponding line indices."""
        layers = {}

        with open(self.filename, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith(";LAYER_CHANGE"):
                    next_line = lines[i + 1]
                    if next_line.startswith(";Z:"):
                        try:
                            z_height = float(next_line.split(":")[1].strip())
                            layers[z_height] = i
                        except ValueError:
                            continue

        return layers

    def print_injected_gcode(self):
        """Scans the G-code file for all injected G-code comments, prints the sections found, and their line numbers."""
        if not self.gcode_content:
            print("Error: G-code content is empty. Please read the G-code file first.")
            return

        # Define the start and end markers for the injected G-code
        start_marker = "; VacuumPnP TOOL G CODE INJECTION START"
        end_marker = "; VacuumPnP TOOL G CODE INJECTION END"

        # Read the G-code file lines to get line numbers
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        start_index = 0
        while True:
            # Find the start marker
            while start_index < len(lines) and start_marker not in lines[start_index]:
                start_index += 1
            if start_index >= len(lines):
                break

            start_line_number = start_index + 1  # Line numbers are 1-based
            start_index += 1  # Move to the next line after the start marker

            # Find the end marker after the start marker
            end_index = start_index
            while end_index < len(lines) and end_marker not in lines[end_index]:
                end_index += 1

            if end_index >= len(lines):
                print(f"Error: Missing end marker for injected G-code starting at line {start_line_number}.")
                return

            end_line_number = end_index + 1  # Line numbers are 1-based

            # Extract the injected G-code section
            injected_gcode_section = ''.join(lines[start_index:end_index]).strip()

            print(f"\nInjected G-code found from line {start_line_number} to {end_line_number}: \n\n{start_marker}\n{injected_gcode_section}\n{end_marker}\n")

            # Move the start_index past the end marker for the next search
            start_index = end_index + 1
