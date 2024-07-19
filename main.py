"""
    (C) 19/07/2024
    University of Leeds, 2024 
    School of Mechanical Engineering

    Custom Sandwiched Slicer Tool for slicing and generating toolpaths for the AMPI
    machine with custom tools.

    Written by Pralish Satyal
    el19ps@leeds.ac.uk
"""

# Import Relevent Libraries
from lib.super_slicer import SuperSlicer
from lib.utils import Utils

# Main Engine
def run():
    config_path = 'static/config.yaml'
    config = Utils.read_yaml(config_path)
    slicer = SuperSlicer(config)
    slicer.slice_gcode()

# Main Implementation
if __name__ == "__main__":
    run()
