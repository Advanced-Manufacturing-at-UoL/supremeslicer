import yaml
import re

class Utils:
    @staticmethod
    def read_yaml(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            # Replace single backslashes with double backslashes
            content = re.sub(r'\\', r'\\\\', content)
            return yaml.safe_load(content)