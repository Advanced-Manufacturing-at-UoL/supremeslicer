# Import Relevent Libraries
from lib.super_slicer import SuperSlicer
from lib.utils import Utils


"""A class for running the Main Engine Client for CLI and UI"""
class MainEngine:    

    # Initialise the class
    def __init__(self):
        self.start_time = None
        
        # Initialise other settings
        config = Utils.read_yaml('static/config.yaml')
        self.slicer = SuperSlicer(config)
    
    # Start the timer
    def start(self):
        self.start_time = Utils.start_timer()
    
    # Stop the timer
    def stop(self):
        Utils.stop_timer(self.start_time)

    # Run the slicer path
    def _run_slicer(self):
        self.start()
        self.slicer.slice_gcode()
        self.stop()

    def cli(self):
        print("Welcome to the SupremeSlicer\n")
        print("Please ensure that you have read the README and have correctly")
        print("added a config.yaml file under the static repository")

        self.user_in = int(input(print("What would you like to do?")))

        print("1. Slice a g-code file")
        print("2.Exit_____________\n")
        print("___________________")
        if self.user_in == 1:
            MainEngine._run_slicer()
        elif self.user_in == 2:
            print("Exitting SupremeSlicer\n")
            Utils.sleep(2)
            Utils.exit_on('Thank you\n')
        else:
            print("Invalid option chosen!")
