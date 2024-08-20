import yaml
import re
import time
import sys
import os

"""Utils class for running utility functions"""
class Utils:
    @staticmethod
    def read_yaml(file_path):
        try:

            absolute_path = Utils.get_resource_path(file_path)

            with open(absolute_path, 'r') as file:
                content = file.read()

                # Replace single backslashes with double backslashes
                content = re.sub(r'\\', r'\\\\', content)
                return yaml.safe_load(content)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            sys.exit(1)

    @staticmethod
    def print_yaml(file_path):
        """
        Reads and prints the YAML file content with indentation to show structure.
        
        :param file_path: The path to the YAML file.
        """
        yaml_data = Utils.read_yaml(file_path)
        Utils._print_yaml_recursive(yaml_data, level = 0)

    def _print_yaml_recursive(yaml_data, level=0):
        """
        Recursively print YAML data with indentation to show structure.

        :param yaml_data: The YAML data to print.
        :param level: The current level of indentation.
        """
        indent = ' ' * (level * 4)
        if isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                print(f"{indent}{key}:")
                Utils._print_yaml_recursive(value, level + 1)
        elif isinstance(yaml_data, list):
            for index, item in enumerate(yaml_data):
                print(f"{indent}- Item {index + 1}:")
                Utils._print_yaml_recursive(item, level + 1)
        else:
            print(f"{indent}{yaml_data}")

    @staticmethod
    def start_timer():
        return time.time()

    @staticmethod
    def stop_timer(start_time):
        elapsed_time = time.time() - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds")

    @staticmethod
    def sleep(sleep_time):
        try:
            time.sleep(float(sleep_time))
        except ValueError:
            print("Invalid sleep time.")

    @staticmethod
    def exit_on(message):
        print(message)
        time.sleep(1)
        sys.exit()
    
    @staticmethod
    def get_resource_path(relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
