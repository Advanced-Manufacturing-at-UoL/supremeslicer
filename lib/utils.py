import yaml
import re
import time
import sys

class Utils:
    @staticmethod
    def read_yaml(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            # Replace single backslashes with double backslashes
            content = re.sub(r'\\', r'\\\\', content)
            return yaml.safe_load(content)
    
    @staticmethod
    def start_timer():
        return time.time()
    
    @staticmethod
    def stop_timer(start_time):
        elapsed_time = time.time() - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds")

    @staticmethod
    def sleep(sleep_time):
        time.sleep(float(sleep_time))
        print(f"Slept for {sleep_time} seconds\n")

    @staticmethod
    def exit_on(message):
        print(str(message))
        time.sleep(1)
        sys.exit()