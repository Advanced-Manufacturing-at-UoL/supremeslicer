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
from lib.utils import Utils
import traceback
import logging

logging.basicConfig(filename = Utils.get_resource_path('error_log.txt'), level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        main_client = MainEngine()
        main_client.cli()
    except Exception as e:
        # Log the exception with traceback
        logging.error("An error occurred: %s", str(e), exc_info=True)
        # Optionally, print the traceback to the console as well
        print("An error occurred. Please check the error_log.txt file for more details.")
        traceback.print_exc()
    finally:
        # Pause the console so it doesn't close immediately
        input("Press any key to close...")

if __name__ == "__main__":
    main()
