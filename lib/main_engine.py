import os

from lib.utils import Utils
from lib.super_slicer import SuperSlicer
from lib.simulation import SimulationProcessor
from lib.animation import ToolpathAnimator
from tools.vacuum_pnp import VacuumPnP


class MainEngine:
    """Main Engine Class for running the overall program"""
    def __init__(self):
        self.start_time = None
        self.config = Utils.read_yaml(r'configs/config.yaml')
        self.slicer = SuperSlicer(self.config)    
        self.vacuum_pnp_tool = None
        self.filename = None

    def start(self):
        """Method to start timer"""
        self.start_time = Utils.start_timer()

    def stop(self):
        """Method to stop timer"""
        Utils.stop_timer(self.start_time)

    def _output_doc(self):
        """Output documentation to the user"""
        Utils.sleep(0.5)
        print("\nThis tool was made by Pralish Satyal and can slice an STL, converting it to GCODE\n")
        Utils.sleep(0.5)
        print("Unlike other slicers, this one can add custom G-Code for custom tools")
        Utils.sleep(0.5)
        print("as well as displaying the overall custom toolpaths per each tool.")
        Utils.sleep(1.5)

        print("Custom tools include the general extruder, the VacuumPnP tool, the screwdriver and the gripper.")
        print("In this version, only the extruder and Vacuum Tool work\n")
        Utils.sleep(1.5)

        print("Prior to running the code, ensure you have read the README and have selected the correct settings")
        Utils.sleep(0.5)
        print("within the configs directory and the tools directory")
        Utils.sleep(0.5)
        print("Use the simulation tool to see each layer better (with the toolpath)")
        Utils.sleep(0.5)
        print("Use the animation tool quickly obtain a render\n")
        print("Good luck and enjoy the software!\n")
        Utils.sleep(1)

    def _run_slicer(self):
        """Run the native Supreme Slicer"""
        self.start()
        self.slicer.slice_gcode()
        self.stop()
        print("\n")

    def _output_folder(self):
        """Access the directories from the configuration file"""
        input_stl_path = self.config['input_stl']
        output_directory = self.config['output_dir']

        base_filename = os.path.splitext(os.path.basename(input_stl_path))[0] # Extract the base filename
        expected_gcode_file = f"{base_filename}.gcode" # Construct the expected G-code filename
        output_gcode_path = os.path.join(output_directory, expected_gcode_file) # Full path with base and filename

        if not os.path.exists(output_gcode_path):
            print(f"No corresponding G-code file found for {input_stl_path} in the output directory.")
            return

        self.filename = output_gcode_path
        self.output_directory = output_directory

    def _vacuum_tool(self):
        """Load Vacuum Tool Menu Options"""
        print("Loading VacuumPnP tool\n")
        config_file = Utils.get_resource_path('tools/vacuum_config.yaml')

        output_directory = self.config['output_dir']
        print(f"Output directory is:{output_directory}")
        print(f"Found G-code file: {self.filename}")

        self.vacuum_pnp_tool = VacuumPnP(self.filename, config_file)

        print("\nWould you like to...")
        print("1. Generate and inject Gcode")
        print("2. Read Gcode file output")

        user_in = int(input())
        if user_in == 1:
            self.vacuum_pnp_tool.read_gcode()
            self.vacuum_pnp_tool.generate_gcode()
            height = float(input("Enter the height to inject the G-code: "))
            output_path = output_directory
            self.vacuum_pnp_tool.inject_gcode_at_height(height, output_path)
        elif user_in == 2:
            self.vacuum_pnp_tool.read_gcode()
            self.vacuum_pnp_tool.print_injected_gcode()
        else:
            print("Invalid option. Please select 1 or 2.")

    def _run_tools(self):
        """Render Tool Option Menu"""
        print("Select a tool to enter:")
        print("1. VacuumPnP")
        print("2. Screwdriver")
        print("3. Gripper")
        print("4. Exit\n")
        
        # Get the folder and file path
        self._output_folder()

        user_in = int(input())
        if user_in == 1:
            self._vacuum_tool()
        else:
            print("\nTool not programmed yet. Sorry!\n")

    def _run_simulation(self):
        """Render simulation menu for simulating toolpaths"""
        try:
            print("1. Plot Original Toolpath")
            print("2. Plot Vacuum Toolpath")
            user_in = int(input("Generate original or tool-specific toolpath?"))

            self._output_folder() # Retrieve the output folder and file
            simulation_processor = SimulationProcessor(self.filename)

            if user_in == 1:
                simulation_processor.plot_original_toolpath()
                print("Completed plotting original toolpath.\n")
            elif user_in == 2:
                simulation_processor.plot_vacuum_toolpath()
                print("Completed plotting vacuum toolpath.\n")
            else:
                print("Invalid selection. Please choose 1 or 2.\n")
        except ValueError as ve:
            raise ValueError(f"Value error: {ve}")
        except FileNotFoundError as fnfe:
            raise FileNotFoundError(f"File not found error: {fnfe}")
        except IOError as ioe:
            raise IOError(f"IO error: {ioe}")
        except Exception as e:
            raise(f"An unexpected error occurred: {e}")

    def _run_animation(self):
        """Render animation menu for plotting layer by layer animation."""
        try:
            print("1. Output rendered simulation")
            print("2. Output final frame to file")
            print("3. Output entire animation as GIF")
            user_in = int(input("Please choose an option\n"))

            self._output_folder() # Retrieve the output folder

            if user_in == 1:
                print("Plotting Original toolpath")
                animator = ToolpathAnimator(self.filename)
                animator.parse_gcode()
                animator.animate_toolpath()
            elif user_in == 2:
                print("\nSaving final Layer")
                animator = ToolpathAnimator(self.filename)
                animator.parse_gcode()
                file_location = self.output_directory + '/final_layer.gif'
                animator.save_final_layer(file_location)
            elif user_in == 3:
                print("\nSaving entire animation. This will take a few minutes.")
                animator = ToolpathAnimator(self.filename)
                animator.parse_gcode()
                file_location = self.output_directory +'/render.gif'
                animator.save_animation(file_location)
            else:
                print("Invalid selection. Please choose 1 or 2.")
        except ValueError as ve:
            raise ValueError(f"Value error: {ve}")
        except FileNotFoundError as fnfe:
            raise FileNotFoundError(f"File not found error: {fnfe}")
        except IOError as ioe:
            raise IOError(f"IO error: {ioe}")
        except Exception as e:
            raise(f"An unexpected error occurred: {e}")

    def _read_config(self):
        """Method to read SupremeSlicer config file"""
        Utils.sleep(1)
        self.start()
        print("\n")
        Utils.print_yaml(r'configs\config.yaml')
        self.stop()
        print("\n")

    def cli(self):
        """Command-line interface for the SupremeSlicer application."""
        print("\nWelcome to the SupremeSlicer\n")
        print("Please ensure that you have read the README and have correctly")
        print("added a config.yaml file under the configs repository")

        while True:
            print("0. Show documentation")
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

            if user_in == 0:
                self._output_doc()
            elif user_in == 1:
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
