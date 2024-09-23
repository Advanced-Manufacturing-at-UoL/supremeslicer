import os

from lib.utils import Utils
from lib.stl_viewer import STLViewer
from lib.prusa_slicer import PrusaSlicer
from lib.simulation import SimulationProcessor
from lib.animation import ToolpathAnimator
from tools.vacuum_pnp import VacuumPnP
from tools.screwdriver import ScrewDriver
from tools.gripper import Gripper

class MainEngine:
    """Main Engine Class for running the overall program"""
    def __init__(self):
        self.config = Utils.read_yaml(r'configs/config.yaml')
        self.slicer = PrusaSlicer(self.config)    
        self.vacuum_pnp_tool = None
        self.screwdriver_tool = None
        self.gripper_tool = None
        self.filename = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~DOCUMENTATION AND BACK-END~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
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

    def _read_config(self):
        """Method to read SupremeSlicer config file"""
        Utils.sleep(1)
        start_time = Utils.start_timer()
        print("\n")
        Utils.print_yaml(Utils.get_resource_path(r'configs\config.yaml'))
        Utils.stop_timer(start_time)
        print("\n")

    def _run_slicer(self):
        """Run the native Supreme Slicer"""
        start_time = Utils.start_timer()
        self.slicer.slice_gcode()
        Utils.stop_timer(start_time)
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~VACUUM TOOL IMPLEMENTATION~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def _vacuum_tool(self):
        """Load Vacuum Tool Menu Options"""
        print("Loading VacuumPnP tool\n")
        self.config_file = Utils.get_resource_path('tools/vacuum_config.yaml')

        self.output_directory = self.config['output_dir']
        print(f"Output directory is:{self.output_directory}")
        print(f"Found G-code file: {self.filename}")

        print("\nWould you like to...")
        print("1. Generate and inject Gcode")
        print("2. Read Gcode file output")
        print("3. Render STL Viewer and auto-inject coordinate")
        self.vacuum_pnp_tool = VacuumPnP(self.filename, self.config_file)
        user_in = int(input())

        if user_in == 1:
            self.vacuum_pnp_tool.read_gcode()
            self.vacuum_pnp_tool.generate_gcode()
            height = float(input("Enter the height to inject the G-code: "))
            output_path = self.output_directory
            self.vacuum_pnp_tool.inject_gcode_at_height(height, output_path)
        elif user_in == 2:
            self.vacuum_pnp_tool.read_gcode()
            self.vacuum_pnp_tool.print_injected_gcode()
        elif user_in == 3:
            self._run_vacuum_stl_viewer()
        else:
            print("Invalid option. Please select between 1-3.")

    def _run_vacuum_stl_viewer(self):
        """Function to handle backend for STL Viewer within Vacuum Injection tool"""
        bed_shape = "20x75,250x75,250x250,20x250"
        user_in = int(input("\nVacuumPnP Code Injection point: \n1.Nearest Layer to input coordinates\n2.Final Layer with actual coordinates\n"))

        if user_in == 1:
            viewer = STLViewer(self.config['input_stl'], self.filename, self.config, bed_shape)
            viewer.start()
            picked_position = viewer.get_selected_point()
            if picked_position:
                if self.config.get('centre', None):
                    print("Centre position has been given")
                    print("Injecting with offset from centre of position")
                    # Update vacuum_config.yaml with the picked position
                    config = Utils.read_yaml(self.config_file) # Read the file again

                    # # Calculate the offset if the part is no longer in centre of bed
                    part_x, part_y = self.config['centre'].split(',')
                    bed_center_x, bed_center_y = 135, 162

                    # # Dynamic offsets: Distance from bed center to part center
                    offset_x = bed_center_x - float(part_x) # this should be 35
                    offset_y = bed_center_y - float(part_y) # this should be 62

                    # # Adjust the picked positions by the dynamic offsets
                    x_pos = picked_position[0] - offset_x -9.47
                    y_pos = picked_position[1] - offset_y -10.2
                    z_pos = picked_position[2]  + 1
                else:
                    print("Injecting without offset from centre as not given")
                    x_pos = float(f"{picked_position[0]:.3f}") - 9.47
                    y_pos = float(f"{picked_position[1]:.3f}") - 10.2
                    z_pos = float(f"{picked_position[2]:.3f}") + 1

                config['startX'] = f"{x_pos:.2f}"
                config['startY'] = f"{y_pos:.2f}"
                config['startZ'] = f"{z_pos:.2f}"
                # Preparation to write_yaml_function
                key_order = [
                    'zHop_mm',
                    'startX',
                    'startY',
                    'startZ',
                    'suctionState',
                    'endX',
                    'endY',
                    'endZ'
                ]

                # Update configuration
                Utils.write_yaml(self.config_file, config, key_order)
                print("Configuration updated with the selected position.")

                # Continue with the existing functionality
                self.vacuum_pnp_tool.load_config()
                self.vacuum_pnp_tool.read_gcode()
                self.vacuum_pnp_tool.generate_gcode()

                # Inject the g-code at the layer corresponding to that coordinate
                self.vacuum_pnp_tool.inject_gcode_given_coordinates(self.output_directory)
        elif user_in == 2:
            print("Injecting G-Code after the 'END PRINT' Command")
            viewer = STLViewer(self.config['input_stl'], self.filename, self.config, bed_shape)
            viewer.start()
            picked_position = viewer.get_selected_point()
            if picked_position:
                if self.config.get('centre', None):
                    print("Centre position has been given")
                    print("Injecting with offset from centre of position")
                    # Update vacuum_config.yaml with the picked position
                    config = Utils.read_yaml(self.config_file) # Read the file again

                    # # Calculate the offset if the part is no longer in centre of bed
                    part_x, part_y = self.config['centre'].split(',')
                    bed_center_x, bed_center_y = 135, 162

                    # # Dynamic offsets: Distance from bed center to part center
                    offset_x = bed_center_x - float(part_x) # this should be 35
                    offset_y = bed_center_y - float(part_y) # this should be 62

                    # # Adjust the picked positions by the dynamic offsets
                    x_pos = picked_position[0] - offset_x -9.47
                    y_pos = picked_position[1] - offset_y -10.2
                    z_pos = picked_position[2]  + 1
                else:
                    print("Injecting without offset from centre as not given")
                    x_pos = float(f"{picked_position[0]:.3f}") - 9.47
                    y_pos = float(f"{picked_position[1]:.3f}") - 10.2
                    z_pos = float(f"{picked_position[2]:.3f}") + 1

                config['startX'] = f"{x_pos:.2f}"
                config['startY'] = f"{y_pos:.2f}"
                config['startZ'] = f"{z_pos:.2f}"
                # Preparation to write_yaml_function
                key_order = [
                    'zHop_mm',
                    'startX',
                    'startY',
                    'startZ',
                    'suctionState',
                    'endX',
                    'endY',
                    'endZ'
                ]

                # Update configuration
                Utils.write_yaml(self.config_file, config, key_order)
                print("Configuration updated with the selected position.")

                # Continue with the existing functionality
                self.vacuum_pnp_tool.load_config()
                self.vacuum_pnp_tool.read_gcode()
                self.vacuum_pnp_tool.generate_gcode()
                self.vacuum_pnp_tool.inject_gcode_final_layer(self.output_directory)
        else:
            print("Invalid option selected! Select 1-2!")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~GRIPPER TOOL IMPLEMENTATION~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def _gripper(self):
        """Load Vacuum Tool Menu Options"""
        print("Loading Gripper tool\n")
        self.config_file = Utils.get_resource_path('tools/gripper_config.yaml')

        self.output_directory = self.config['output_dir']
        print(f"Output directory is:{self.output_directory}")
        print(f"Found G-code file: {self.filename}")

        print("\nWould you like to...")
        print("1. Read Gcode file output")
        print("2. Inject the gripper tool code using your parsed values")

        self.gripper_tool = Gripper(self.filename, self.config_file)
        user_in = int(input())

        if user_in == 1:
            self.gripper_tool.read_gcode()
            self.gripper_tool.print_injected_gcode()
        elif user_in == 2:
            self.gripper_tool.load_config()
            self.gripper_tool.read_gcode()
            self.gripper_tool.generate_gcode()
            self.gripper_tool.inject_gcode_final_layer(self.output_directory)
        else:
            print("Invalid option. Please select between 1-3.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~SCREWDRIVER IMPLEMENTATION~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def _screwdriver(self):
        """Load Screwdriver Tool Menu Options"""
        print("Loading Screwdriver tool\n")
        self.config_file = Utils.get_resource_path('tools/screwdriver_config.yaml')

        self.output_directory = self.config['output_dir']
        print(f"Output directory is:{self.output_directory}")
        print(f"Found G-code file: {self.filename}")

        print("\nWould you like to...")
        print("1. Read Gcode file output")
        print("2. Render STL Viewer and auto-inject coordinate")

        self.screwdriver_tool = ScrewDriver(self.filename, self.config_file)
        user_in = int(input())

        if user_in == 1:
            self.screwdriver_tool.read_gcode()
            self.screwdriver_tool.print_injected_gcode()
        elif user_in == 2:
            self._run_screwdriver_stl_viewer()
        else:
            print("Invalid option. Please select between 1-3.")

    def _run_screwdriver_stl_viewer(self):
        """Function to handle backend for STL Viewer within Vacuum Injection tool"""
        bed_shape = "20x75,250x75,250x250,20x250"
    
        print("Injecting G-Code after the 'END PRINT' Command")
        viewer = STLViewer(self.config['input_stl'], self.filename, self.config, bed_shape)
        viewer.start()
        picked_position = viewer.get_selected_point()
        if picked_position:
            if self.config.get('centre', None):
                print("Centre position has been given")
                print("Injecting with offset from centre of position")
                # Update vacuum_config.yaml with the picked position
                config = Utils.read_yaml(self.config_file) # Read the file again

                # # Calculate the offset if the part is no longer in centre of bed
                part_x, part_y = self.config['centre'].split(',')
                bed_center_x, bed_center_y = 135, 162

                # # Dynamic offsets: Distance from bed center to part center
                offset_x = bed_center_x - float(part_x) # this should be 35
                offset_y = bed_center_y - float(part_y) # this should be 62

                # # Adjust the picked positions by the dynamic offsets
                x_pos = picked_position[0] - offset_x -9.47
                y_pos = picked_position[1] - offset_y -10.2
                z_pos = picked_position[2]  + 1
            else:
                print("Injecting without offset from centre as not given")
                x_pos = float(f"{picked_position[0]:.3f}") - 9.47
                y_pos = float(f"{picked_position[1]:.3f}") - 10.2
                z_pos = float(f"{picked_position[2]:.3f}") + 1

            config['startX'] = f"{x_pos:.2f}"
            config['startY'] = f"{y_pos:.2f}"
            config['startZ'] = f"{z_pos:.2f}"
            # Preparation to write_yaml_function
            key_order = [
                'zHop_mm',
                'startX',
                'startY',
                'startZ',
                'screwType',
            ]

            # Update configuration
            Utils.write_yaml(self.config_file, config, key_order)
            print("Configuration updated with the selected position.")

            # Continue with the existing functionality
            self.screwdriver_tool.load_config()
            self.screwdriver_tool.read_gcode()
            self.screwdriver_tool.generate_gcode()
            self.screwdriver_tool.inject_gcode_final_layer(self.output_directory)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TOOL BAR MENU OPTIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
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
        elif user_in == 2:
            self._screwdriver()
        elif user_in == 3:
            self._gripper()
        elif user_in == 4:
            Utils.exit_on('Thank you for runnning the program\n')
        else:
            print("\nInvalid option selected!\n")

    def _get_part_info(self):
        """Method to get part information"""
        try:
            print("1. Get estimated individual part centre via avg. values")
            print("2. Get height of part from max Z")
            print("3. Get bounding box of the part")
            print("4. Get part's top layer position for Vacuum tool")
            print("5. Get centre of mass for the part")

            user_in = int(input("Please select an option.\n"))
            self._output_folder()
            simulation_processor = SimulationProcessor(self.filename)

            if user_in == 1:
                start_time = Utils.start_timer()
                centre = simulation_processor.get_part_info()
                if centre:
                    print(f"Center of the part: X={centre[0]:.2f}, Y={centre[1]:.2f}, Z={centre[2]:.2f}")
                print("Obtained part information.\n")
                Utils.stop_timer(start_time)
            elif user_in == 2:
                start_time = Utils.start_timer()
                height = simulation_processor.get_part_height()
                if height:
                    print(f"Height of the part: Z={height:.2f}")
                print("Obtained part height.\n")
                Utils.stop_timer(start_time)
            elif user_in == 3:
                start_time = Utils.start_timer()
                bounding_box = simulation_processor.get_bounding_box()
                if bounding_box:
                    print(f"Bounding box of the part: box={bounding_box}")
                print("Obtained part bounding box.\n")
                Utils.stop_timer(start_time)
            elif user_in == 4:
                start_time = Utils.start_timer()
                top_layer = simulation_processor.get_top_layer_info()
                if top_layer:
                    print(f"Top layer of the part: layer={top_layer}")
                print("Obtained part top-layer info.\n")
                Utils.stop_timer(start_time)    
            elif user_in == 5:
                start_time = Utils.start_timer()
                centre_of_mass = simulation_processor.get_centre_of_mass()
                if centre_of_mass:
                    print(f"Centre of mass of the part: {centre_of_mass}")
                print("Obtained part centre of mass info.\n")
                Utils.stop_timer(start_time)                   
            else:
                print("Invalid selection. Please choose from Option 1-3\n")             
        except ValueError as ve:
            raise ValueError(f"Value error: {ve}")
        except FileNotFoundError as fnfe:
            raise FileNotFoundError(f"File not found error: {fnfe}")
        except IOError as ioe:
            raise IOError(f"IO error: {ioe}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~SIMULATOIN OVERVIEW~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def _run_stl_viewer(self):
        """Render the stl visually"""
        try:
            self._output_folder()
            bed_shape = "20x75,250x75,250x250,20x250"
            viewer = STLViewer(self.config['input_stl'], self.filename, self.config, bed_shape)
            viewer.start()
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    def _run_simulation(self):
        """Render simulation menu for simulating toolpaths"""
        try:
            print("1. Plot Original Toolpath")
            print("2. Plot Vacuum Toolpath")
            user_in = int(input("Generate original or tool-specific toolpath?\n"))

            self._output_folder() # Retrieve the output folder and file
            simulation_processor = SimulationProcessor(self.filename)

            if user_in == 1:
                start_time = Utils.start_timer()
                simulation_processor.plot_original_toolpath()
                print("Completed plotting original toolpath.\n")
                Utils.stop_timer(start_time)
            elif user_in == 2:
                start_time = Utils.start_timer()
                simulation_processor.plot_vacuum_toolpath()
                print("Completed plotting vacuum toolpath.\n")
                Utils.stop_timer(start_time)
            else:
                print("Invalid selection. Please choose 1 or 2.\n")
        except ValueError as ve:
            raise ValueError(f"Value error: {ve}")
        except FileNotFoundError as fnfe:
            raise FileNotFoundError(f"File not found error: {fnfe}")
        except IOError as ioe:
            raise IOError(f"IO error: {ioe}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

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
                start_time = Utils.start_timer()
                animator = ToolpathAnimator(self.filename)
                animator.parse_gcode()
                animator.animate_toolpath()
                Utils.stop_timer(start_time)
            elif user_in == 2:
                print("\nSaving final Layer")
                start_time = Utils.start_timer()
                animator = ToolpathAnimator(self.filename)
                animator.parse_gcode()
                file_location = self.output_directory + '/final_layer.png'
                animator.save_final_layer(Utils.get_resource_path(file_location))
                Utils.stop_timer(start_time)
            elif user_in == 3:
                print("\nSaving entire animation. This will take a few minutes.")
                start_time = Utils.start_timer()
                animator = ToolpathAnimator(self.filename)
                animator.parse_gcode()
                file_location = self.output_directory +'/render.gif'
                animator.save_animation(Utils.get_resource_path(file_location))
                Utils.stop_timer(start_time)
            else:
                print("Invalid selection. Please choose 1 or 2.")
        except ValueError as ve:
            raise ValueError(f"Value error: {ve}")
        except FileNotFoundError as fnfe:
            raise FileNotFoundError(f"File not found error: {fnfe}")
        except IOError as ioe:
            raise IOError(f"IO error: {ioe}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    def cli(self):
        """Command-line interface for the SupremeSlicer application."""
        os.system('cls')
        print("\nWelcome to the SupremeSlicer\n")
        print("Please ensure that you have read the README and have correctly")
        print("added a config.yaml file under the configs repository")

        while True:
            print("0. Show documentation")
            print("1. Read Config file")
            print("2. Slice a g-code file")
            print("3. Access tools")
            print("4. Obtain Part informaiton")
            print("5. Run STL Viewer")
            print("6. Create Simulation")
            print("7. Render Animation")
            print("8. Exit\n")

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
                self._get_part_info()
            elif user_in == 5:
                self._run_stl_viewer()
            elif user_in == 6:
                self._run_simulation()
            elif user_in == 7:
                self._run_animation()
            elif user_in == 8:
                print("Exiting SupremeSlicer\n")
                Utils.exit_on('Thank you\n')
            else:
                print("Invalid option chosen!")
