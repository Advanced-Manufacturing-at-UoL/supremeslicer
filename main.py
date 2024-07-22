"""
(C) 19/07/2024
Edited 22/07/2024
University of Leeds, 2024
School of Mechanical Engineering

Custom Sandwiched Slicer Tool for slicing and generating toolpaths for the AMPI
machine with custom tools.

Written by Pralish Satyal
el19ps@leeds.ac.uk
"""

# Import Main Engine Class to run the process thread
from lib.main_engine import MainEngine

def main():
    main_client = MainEngine()
    main_client.cli()

if __name__ == "__main__":
    main()
