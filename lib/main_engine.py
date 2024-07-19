from lib.super_slicer import SuperSlicer
from lib.utils import Utils

class MainEngine:
    def __init__(self):
        self.start_time = None
        self.config = Utils.read_yaml('configs/config.yaml')
        self.slicer = SuperSlicer(self.config)

    def start(self):
        self.start_time = Utils.start_timer()

    def stop(self):
        Utils.stop_timer(self.start_time)

    def _run_slicer(self):
        self.start()
        self.slicer.slice_gcode()
        self.stop()

    def _read_config(self):
        self.start()
        Utils.print_yaml('configs/config.yaml')
        self.stop()

    def cli(self):

        # Starting Message
        print("\nWelcome to the SupremeSlicer\n")
        print("Please ensure that you have read the README and have correctly")
        print("added a config.yaml file under the configs repository")

        while True:
            print("1. Read Config file")
            print("2. Slice a g-code file")
            print("3. Exit\n")
            
            try:
                self.user_in = int(input("Please select an option"))
            except ValueError:
                print("Invalid input. Please enter a number.")
                return

            if self.user_in == 1:
                self._read_config()
            elif self.user_in == 2:
                self._run_slicer()
            elif self.user_in == 3:
                print("Exiting SupremeSlicer\n")
                Utils.sleep(2)
                Utils.exit_on('Thank you\n')
            else:
                print("Invalid option chosen!")
