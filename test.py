import subprocess
import os
from lib.utils import Utils

class SuperSlicer:
    """SuperSlicer Native Slicer handler class"""
    def __init__(self, config):
        self.superslicer_executable = config.get('superslicer_executable')
        self.printer_profile = config.get('printer_profile')
        self.input_stl = config.get('input_stl')
        self.output_dir = config.get('output_dir')

        if not all([self.superslicer_executable, self.printer_profile, self.input_stl, self.output_dir]):
            raise ValueError("Missing one or more configuration parameters.")
        
    def _confirm_input(self):
        """Method to confirm the config.yaml file input"""
        print(f"Slicer config file has been read\n")
        print(f"Super slicer executable path: {self.superslicer_executable}")
        print(f"Printer profile loaded is: {self.printer_profile}")
        print(f"Input STL path: {self.input_stl}")
        print(f"Output directory loaded: {self.output_dir}\n")
        print("\n\n\n\n\n")

    def set_preset(self):
        """Method to save the current configuration preset to a .ini file"""
        command = [
            self.superslicer_executable,
            "--autosave", self.printer_profile
        ]

        print("Executing command:", ' '.join(command))  # Debugging line to check the command

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Command output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during preset configuration: {e}")
            print("Command output:", e.output)
            print("Command stderr:", e.stderr)

    def slice_gcode(self):
        """Method to slice STL and export output to G-code file"""
        output_gcode_path = os.path.join(self.output_dir, os.path.basename(self.input_stl).replace('.stl', '.gcode'))

        # Construct the command with the correct paths
        command = [
            self.superslicer_executable,
            "--load", self.printer_profile,
            "--export-gcode", self.input_stl,
            "--output", output_gcode_path
        ]

        print("Executing command:", ' '.join(command), "\n")  # Debugging line to check the command

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Command output:", result.stdout)
            print("\nSlicing completed successfully.")
            print(f"Please check {self.output_dir} for the G-code file: {os.path.basename(output_gcode_path)}\n")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during slicing: {e}")
            print("Command output:", e.output)
            print("Command stderr:", e.stderr)

if __name__ == "__main__":
    config = Utils.read_yaml(r'configs/config.yaml')
    slicer = SuperSlicer(config)
    
    # Slice the STL to G-code using the provided configuration
    slicer._confirm_input()
    slicer.slice_gcode()
