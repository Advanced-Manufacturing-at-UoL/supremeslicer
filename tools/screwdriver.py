import os
import math
from lib.utils import Utils

class ScrewDriver:
    """Class for handling functions for the ScrewDriver tool"""
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
            self.screwType = config.get('screwType', 0)

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
; ScrewDriver TOOL G CODE INJECTION START
G90 ; Ensure we're using absolute positioning rather than relative
G0 Z{self.zHop_mm:.2f} ; Move to zHop position for clearance
TOOL_PICKUP T=4 ; Pickup the Screwdriver tool
G0 X{self.startX:.2f} Y{self.startY:.2f} ; Move to where you want to suck in X,Y
G0 Z{self.startZ:.2f} ; Lower Z to start position
INSERT_SCREW SCREW={self.screwType} ; Insert Screw
G0 Z{self.zHop_mm:.2f} ; Move to zHop position for clearance
TOOL_PICKUP T=0 ; Pickup the Extruder tool again, but this only works for single extruder
G91 ; Set back to relative positioning 
; ScrewDriver TOOL G CODE INJECTION END
;-----------------------------------------------
"""
        print("G-code injection generated.")

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
        start_marker = "; ScrewDriver TOOL G CODE INJECTION START"
        end_marker = "; ScrewDriver TOOL G CODE INJECTION END"

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
