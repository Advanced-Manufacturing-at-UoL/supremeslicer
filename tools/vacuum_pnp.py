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
G90 ; Ensure we're using absolute positioning rather than relative
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
        target_x = self.startX
        target_y = self.startY
        target_z = self.startZ

        print("The targets that we have are")
        print(f"G1 X{target_x} Y{target_y} Z{target_z}")

        # Find the closest line to the target coordinates
        injection_point = self._find_closest_line(target_x, target_y, target_z)
        if injection_point == -1:
            print("Error: Could not find a suitable injection point based on coordinates.")
            return

        print(f"Injecting at closest line: {injection_point} (Closest coordinates)")

        with open(self.filename, 'r') as f:
            lines = f.readlines()

        custom_gcode_lines = self.injected_gcode.splitlines()
        lines.insert(injection_point + 1, '\n'.join(custom_gcode_lines) + '\n')

        # Define the output path
        output_file = Utils.get_resource_path(os.path.join(output_path, os.path.basename(self.filename)))
        
        with open(output_file, 'w') as f:
            f.writelines(lines)

        print(f"G-code injected and saved to {output_file}\n")

    def _find_closest_line(self, target_x, target_y, target_z):
        """
        Finds the closest line in the G-code to the given coordinates (x, y, z).
        Returns the line index where the closest coordinates are found.
        """
        closest_distance = float('inf')
        closest_index = -1

        with open(self.filename, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith('G0') or line.startswith('G1'):
                    coords = self._parse_gcode_line(line)
                    if coords:
                        x, y, z = coords
                        distance = abs(x - target_x) + abs(y - target_y) + abs(z - target_z)
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_index = i

            return closest_index

    def _parse_gcode_line(self, line):
        """
        Parses a G-code line to extract X, Y, Z coordinates.
        Returns a tuple (x, y, z) or None if the coordinates are not present.
        """
        x = y = z = None
        parts = line.split()
        for part in parts:
            if part.startswith('X'):
                x = float(part[1:])
            elif part.startswith('Y'):
                y = float(part[1:])
            elif part.startswith('Z'):
                z = float(part[1:])
        if x is not None and y is not None and z is not None:
            return (x, y, z)
        return None

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
