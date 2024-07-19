from lib.super_slicer import SuperSlicer
from lib.utils import Utils
from tools.vacuum_pnp import VacuumPnP

class MainEngine:
    def __init__(self):
        self.start_time = None
        self.config = Utils.read_yaml('configs/config.yaml')
        self.slicer = SuperSlicer(self.config)
        self.vacuum_pnp_tool = None

    def start(self):
        self.start_time = Utils.start_timer()

    def stop(self):
        Utils.stop_timer(self.start_time)

    def _run_slicer(self):
        self.start()
        self.slicer.slice_gcode()
        self.stop()

    def _vacuum_tool(self):
        print("Loading VacuumPnP tool\n")
        filename = input("Enter the path to the G-code file: ")
        config_file = 'tools/vacuum_config.yaml'

        self.vacuum_pnp_tool = VacuumPnP(filename, config_file)
        
        print("Would you like to...")
        print("1. Generate and inject Gcode")
        print("2. Read Gcode file output")

        user_in = int(input())
        if user_in == 1:
            self.vacuum_pnp_tool.read_gcode()
            self.vacuum_pnp_tool.generate_gcode()
            layer = int(input("Enter the layer number to inject the G-code: "))
            output_path = input("Enter the path for the output file: ")
            self.vacuum_pnp_tool.inject_gcode(layer, output_path)
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
            print("4. Exit\n")
            
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
                print("Exiting SupremeSlicer\n")
                Utils.sleep(2)
                Utils.exit_on('Thank you\n')
            else:
                print("Invalid option chosen!")
