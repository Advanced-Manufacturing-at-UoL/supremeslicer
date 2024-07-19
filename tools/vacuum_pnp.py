from lib.utils import Utils

class VacuumPnP:
    def __init__(self, filename, config_file):
        """
        Initialize the VacuumPnP Tool with a G-code file and a configuration file.

        :param filename: Path to the G-code file.
        :param config_file: Path to the YAML configuration file.
        """
        self.filename = filename
        self.config_file = config_file
        self.gcode_content = None
        self.injected_gcode = None

        # Load configuration from YAML file
        self.load_config()

    def load_config(self):
        """
        Loads the parameters from the YAML configuration file.
        """
        try:
            with open(self.config_file, 'r') as file:
                config = Utils.read_yaml(self.config_file)
                self.zHop_mm = config.get('zHop_mm', 5.0)
                self.startX = config.get('startX', 10.0)
                self.startY = config.get('startY', 20.0)
                self.startZ = config.get('startZ', 30.0)
                self.suctionState = config.get('suctionState', 1)
                self.endX = config.get('endX', 40.0)
                self.endY = config.get('endY', 50.0)
                self.endZ = config.get('endZ', 60.0)
                print("Configuration loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Configuration file not found: {self.config_file}")
        except Exception as e:
            print(f"Error: {e}")

    def read_gcode(self):
        """
        Reads the G-code file and stores its content.
        """
        try:
            with open(self.filename, 'r') as file:
                self.gcode_content = file.read()
                print("G-code file read successfully.")
        except FileNotFoundError:
            print(f"Error: G-code file not found: {self.filename}")
        except IOError as e:
            print(f"Error reading G-code file: {e}")

    def generate_gcode(self):
        """
        Generates the G-code injection based on the parameters from the YAML configuration.
        """
        self.injected_gcode = f""";-----------------------------------------------
; VacuumPnP TOOL G CODE INJECTION START
G0 Z{self.zHop_mm:.2f} ; Move to zHop position for clearance
G0 X{self.startX:.2f} Y{self.startY:.2f}
G0 Z{self.startZ:.2f} ; Move to startPosition
M98 P{self.suctionState} ; Execute suction state
G0 X{self.endX:.2f} Y{self.endY:.2f}
G0 Z{self.endZ:.2f} ; Move to endPosition
G0 Z{self.zHop_mm:.2f} ; Move to zHop position for clearance
; VacuumPnP TOOL G CODE INJECTION END
;-----------------------------------------------
"""
        print("G-code injection generated.")

    def inject_gcode(self, layer, output_path):
        """
        Injects the generated G-code at the specified layer into a new file.

        :param layer: The layer number where the G-code should be injected.
        :param output_path: Path for the output file with injected G-code.
        """
        if not self.gcode_content:
            print("Error: G-code content is empty. Please read the G-code file first.")
            return
        
        if not self.injected_gcode:
            print("Error: No G-code injection generated. Please generate G-code first.")
            return

        # Insert the generated G-code at the specified layer
        lines = self.gcode_content.splitlines()
        layer_index = next((i for i, line in enumerate(lines) if f";LAYER:{layer}" in line), -1)
        if layer_index != -1:
            lines.insert(layer_index + 1, self.injected_gcode)
            with open(output_path, 'w') as file:
                file.write('\n'.join(lines))
            print(f"G-code injected at layer {layer} and written to {output_path}.")
        else:
            print(f"Layer {layer} not found in the G-code file.")

    def print_injected_gcode(self):
        """
        Prints the generated and injected G-code to the screen.
        """
        if self.injected_gcode:
            print("Injected G-code:\n")
            print(self.injected_gcode)
        else:
            print("No injected G-code to print. Please generate G-code first.")
