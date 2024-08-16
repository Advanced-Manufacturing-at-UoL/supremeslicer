from lib.super_slicer import SuperSlicer
from lib.utils import Utils
from tools.vacuum_pnp import VacuumPnP
from lib.simulation import SimulationProcessor
from lib.animation import ToolpathAnimator
import os
import yaml

"""Main Engine Class for running the overall program"""
class MainEngine:
    def __init__(self):
        self.start_time = None
        self.config = Utils.read_yaml('configs/config.yaml')
        self.slicer = SuperSlicer(self.config)    
        self.vacuum_pnp_tool = None
        self.filename = None

    def start(self):
        self.start_time = Utils.start_timer()

    def stop(self):
        Utils.stop_timer(self.start_time)

    def _run_slicer(self):
        self.start()
        self.slicer.slice_gcode()
        self.stop()


    def _output_folder(self):
        # Access the input STL and output directory from the loaded config
        input_stl_path = self.config['input_stl']
        output_directory = self.config['output_dir']

        # Extract the base filename (without extension) from the input STL file path
        base_filename = os.path.splitext(os.path.basename(input_stl_path))[0]

        # Construct the expected G-code filename
        expected_gcode_file = f"{base_filename}.gcode"

        # Full path of the expected G-code file in the output directory
        output_gcode_path = os.path.join(output_directory, expected_gcode_file)

        if not os.path.exists(output_gcode_path):
            print(f"No corresponding G-code file found for {input_stl_path} in the output directory.")
            return

        self.filename = output_gcode_path
        print(f"Found G-code file: {self.filename}")


    def _vacuum_tool(self):
        print("Loading VacuumPnP tool\n")
        config_file = 'tools/vacuum_config.yaml'

        output_directory = 'output/'

        # Get list of files matching the pattern
        gcode_files = [f for f in os.listdir(output_directory) if f.endswith('.gcode')]

        if not gcode_files:
            print("No .gcode files found in the input directory.")
            return

        # Assuming there's only one .gcode file or you want to process the first one found
        self.filename = os.path.join(output_directory, gcode_files[0])
        print(f"Found G-code file: {self.filename}")

        self.vacuum_pnp_tool = VacuumPnP(self.filename, config_file)

        print("Would you like to...")
        print("1. Generate and inject Gcode")
        print("2. Read Gcode file output")

        user_in = int(input())
        if user_in == 1:
            self.vacuum_pnp_tool.read_gcode()
            self.vacuum_pnp_tool.generate_gcode()
            height = float(input("Enter the height to inject the G-code: "))
            output_path = 'output'
            self.vacuum_pnp_tool.inject_gcode_at_height(height, output_path)
        elif user_in == 2:
            self.vacuum_pnp_tool.print_injected_gcode()
        else:
            print("Invalid option. Please select 1 or 2.")

    def _run_tools(self):
        print("Select a tool to enter:")
        print("1. VacuumPnP")
        print("2. Screwdriver")
        print("3. Gripper")
        print("4. Exit\n")

        user_in = int(input())
        if user_in == 1:
            self._vacuum_tool()
        else:
            print("Tool not programmed yet. Sorry!")

    def _run_simulation(self):
        """Runs the simulation for plotting the toolpath."""
        try:
            print("1. Plot Original Toolpath")
            print("2. Plot Vacuum Toolpath")
            user_in = int(input("Generate original or tool-specific toolpath?"))

            # Retrieve the output folder and file
            self._output_folder()

            # Initialize the simulation processor
            simulation_processor = SimulationProcessor(self.filename)

            if user_in == 1:
                simulation_processor.plot_original_toolpath()
                print("Completed plotting original toolpath.")
            elif user_in == 2:
                simulation_processor.plot_vacuum_toolpath()
                print("Completed plotting vacuum toolpath.")
            else:
                print("Invalid selection. Please choose 1 or 2.")

        except ValueError as ve:
            print(f"Value error: {ve}")
        except FileNotFoundError as fnfe:
            print(f"File not found error: {fnfe}")
        except IOError as ioe:
            print(f"IO error: {ioe}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def _run_animation(self):
        """Runs the simulation for plotting the toolpath."""
        try:
            print("1. Output rendered simulation")
            print("2. Output final frame to file")
            print("3. Output entire animation as GIF")
            user_in = int(input("Please choose an option\n"))

            # Retrieve the output folder and file
            self._output_folder()

            # Initialise animator
            animator = ToolpathAnimator(self.filename)
            
            animator.parse_gcode()
            
            if user_in == 1:
                animator.animate_toolpath()
                print("Completed plotting original toolpath.")
            elif user_in == 2:
                animator.save_final_layer('output/final_layer.gif')
            elif user_in == 3:
                animator.save_animation('output/render.gif')
            else:
                print("Invalid selection. Please choose 1 or 2.")

        except ValueError as ve:
            print(f"Value error: {ve}")
        except FileNotFoundError as fnfe:
            print(f"File not found error: {fnfe}")
        except IOError as ioe:
            print(f"IO error: {ioe}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def _read_config(self):
        Utils.sleep(1)
        self.start()
        Utils.print_yaml('configs/config.yaml')
        self.stop()

    def cli(self):
        """
        Command-line interface for the SupremeSlicer application.
        """
        print("\nWelcome to the SupremeSlicer\n")
        print("Please ensure that you have read the README and have correctly")
        print("added a config.yaml file under the configs repository")

        while True:
            print("1. Read Config file")
            print("2. Slice a g-code file")
            print("3. Access tools")
            print("4. Create Simulation")
            print("5. Render Animation")
            print("6. Exit\n")

            try:
                user_in = int(input("Please select an option\n"))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if user_in == 1:
                self._read_config()
            elif user_in == 2:
                self._run_slicer()
            elif user_in == 3:
                self._run_tools()
            elif user_in == 4:
                self._run_simulation()
            elif user_in == 5:
                self._run_animation()
            elif user_in == 6:
                print("Exiting SupremeSlicer\n")
                Utils.exit_on('Thank you\n')
            else:
                print("Invalid option chosen!")
