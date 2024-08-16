"""
(C) 19/07/2024
Edited 07/08/2024
University of Leeds, 2024
School of Mechanical Engineering

Custom Sandwiched Slicer Tool for slicing and generating toolpaths for the AMPI
machine with custom tools.

Written by Pralish Satyal
el19ps@leeds.ac.uk
P.Satyal@leeds.ac.uk

pralishbusiness@gmail.com
"""

# Import Main Engine Class to run the process thread
from lib.main_engine import MainEngine
import traceback
import logging

logging.basicConfig(filename = 'error_log.txt', level=logging.ERROR)

def main():
    try:
        main_client = MainEngine()
        main_client.cli()
    except Exception as e:
        logging.error("An error occured", exc_info=True)


if __name__ == "__main__":
    main()
