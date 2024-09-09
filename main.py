"""
(C) 19/07/2024
Editted 09/09/2024
University of Leeds, 2024
School of Mechanical Engineering

Custom Slicer Tool for slicing and generating toolpaths for the AMPI
machine with custom tools. Current verion is V1.3.X. This code has a
toolpath renderer as well as a animation tool for rendering the toolpath.

Fully Written and Designed by Pralish Satyal
el19ps@leeds.ac.uk
P.Satyal@leeds.ac.uk
pralishbusiness@gmail.com
"""

import traceback
import logging # Import debugging methods
from lib.main_engine import MainEngine # Import classes to run main_engine client
from lib.utils import Utils

def main():
    try:
        main_client = MainEngine()
        main_client.cli()
    except Exception as e:
        logging.basicConfig(filename = Utils.get_resource_path('error_log.txt'), level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error("An error occurred: %s", str(e), exc_info=True)
        print("An error occurred. Please check the error_log.txt file for more details.")
        traceback.print_exc()
    finally:
        input("Press any key to close...")

if __name__ == "__main__":
    main()
