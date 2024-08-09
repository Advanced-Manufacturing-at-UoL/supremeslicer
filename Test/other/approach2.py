import subprocess
import os

# Path to the Camotics executable on Windows
# Make sure this path matches the installation location of Camotics
camotics_path = r"C:\Program Files (x86)\CAMotics\camotics.exe"

# Path to the G-code file
gcode_file_path = r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\supremeslicer\output\box.gcode'

# Check if the G-code file exists
if not os.path.isfile(gcode_file_path):
    raise FileNotFoundError(f"The G-code file {gcode_file_path} does not exist.")

# Command to visualize the G-code with Camotics
visualize_tool_path_command = [
    camotics_path,
    gcode_file_path
]

# Execute the command
try:
    print("trying to run code")
    print(f"campotics_path = {camotics_path}\n")
    print(f"gcode file path = {gcode_file_path}\n")
    subprocess.run(visualize_tool_path_command, check=True)
except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
