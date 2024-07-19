import subprocess

class SuperSlicer:
    def __init__(self, config):
        self.superslicer_executable = config['superslicer_executable']
        self.printer_profile = config['printer_profile']
        self.input_stl = config['input_stl']
        self.output_dir = config['output_dir']

    def slice_gcode(self):
        command = [
            self.superslicer_executable,
            "--load", self.printer_profile,
            "--export-gcode", self.input_stl,
            "--output", self.output_dir
        ]

        try:
            subprocess.run(command, check=True)
            print("Slicing completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
