"""
    Custom Sandwiched Slicer Tool for running Slicer and Creating Simulation for models
"""

# Import Relevent Libraries
import subprocess

#
#"C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\SuperSlicer_2.5.59.13_win64_240701\SuperSlicer_2.5.59.13_win64_240701\superslicer.exe"
#--load "C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\Prusa\PrusaSlicer_config_bundle-010724.ini"
#--export-gcode "C:\Users\prali\Downloads\3dbenchy.stl" --output "C:\Users\prali\Downloads"


# File Paths 
superslicer_executable = r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\SuperSlicer_2.5.59.13_win64_240701\SuperSlicer_2.5.59.13_win64_240701\superslicer.exe'
printer_profile = r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\Prusa\PrusaSlicer_config_bundle-010724.ini'
input_stl = r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\3dbenchy.stl'
output_dir = r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer' 

# Create command to execute within the terminal
command = [
    superslicer_executable,
    "--load", printer_profile,
    "--export-gcode", input_stl,
    "--output", output_dir
]

# Main Engine
def run():
    try:
        subprocess.run(command, check=True)
        print("Slicing completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")


# Main Implementation
if __name__ == "__main__":
    run()