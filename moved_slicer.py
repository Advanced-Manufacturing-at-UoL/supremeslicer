import subprocess
import os
import sys, time
from lib.utils import Utils

class PrusaSlicer:
    """PrusaSlicer Native Slicer handler class"""
    def __init__(self):
        config = Utils.read_yaml(r'test_config.yaml')
        self.prusaslicer_executable = config.get('prusaslicer_executable')
        self.printer_profile = config.get('printer_profile')
        self.translation = config.get('translation')
        self.input_stl = config.get('input_stl')
        self.output_dir = config.get('output_dir')

        if not all([self.prusaslicer_executable, self.printer_profile, self.input_stl, self.output_dir]):
            raise ValueError("Missing one or more configuration parameters.")

    def _confirm_input(self):
        """Method to confirm the config.yaml file input"""
        print(f"Slicer config file has been read\n")
        print(f"Prusa slicer executable path: {self.prusaslicer_executable}")
        print(f"Printer profile loaded is: {self.printer_profile}")
        print(f"Input STL path: {self.input_stl}")
        print(f"Output directory loaded: {self.output_dir}\n")
        print("\n\n\n\n\n")

    def set_preset(self):
        """Method to save the current configuration preset to a .ini file"""
        command = [
            self.prusaslicer_executable,
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

        # slic3r -g my_model.stl --center 40,40

        command = [
            self.prusaslicer_executable,
            "--load", self.printer_profile,
            "-g", r"C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\SupremeSlicer\supremeslicer\input\xyzCalibration_cube.stl",
            "--center", "100,100",
            "--export-gcode", self.input_stl,
            "--output", output_gcode_path,
        ]

        print("Executing command:", ' '.join(command), "\n")

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Command output:", result.stdout)
            print("\nSlicing completed successfully.")
            print(f"Please check {self.output_dir} for the G-code file: {os.path.basename(output_gcode_path)}\n")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during slicing: {e}")
            print("Command output:", e.output)
            print("Command stderr:", e.stderr)



def main():
    """Run the native Supreme Slicer"""
    slicer = PrusaSlicer()

    print("1. Slice file with translation")
    print("2. Exit")
    user_in = int(input("Would you like to run the slicer?"))

    if user_in == 1:
        start_time = Utils.start_timer()
        slicer.slice_gcode()
        Utils.stop_timer(start_time)
        print("\n")
    elif user_in == 2:
        print("Exitting program")
        time.sleep(1)
        sys.exit()
    else:
        print("Invalid option selected, please enter just 1 or 2!\n")


# Main Space to run our code
if __name__ == "__main__":
    print("Starting program\n")
    main()
