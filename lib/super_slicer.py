import subprocess


class SuperSlicer:
    """SuperSlicer Native Slicer handler class"""
    def __init__(self, config):
        self.superslicer_executable = config.get('superslicer_executable')
        self.printer_profile = config.get('printer_profile')
        self.input_stl = config.get('input_stl')
        self.output_dir = config.get('output_dir')

        if not all([self.superslicer_executable, self.printer_profile, self.input_stl, self.output_dir]):
            raise ValueError("Missing one or more configuration parameters.")

    def slice_gcode(self):
        """Method to slice stl and export output to gcode file"""
        command = [
            self.superslicer_executable,
            "--load", self.printer_profile,
            "--export-gcode", self.input_stl,
            "--output", self.output_dir
        ]

        try:
            subprocess.run(command, check=True)
            print("\nSlicing completed successfully.")
            print(f"Please check {self.output_dir}\n")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
