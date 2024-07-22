
"""
    Test Script to find the layer height from the print settings file
    
    Written by Pralish Satyal
    11/07/2024
"""

# Import Relevent Libraries
import traceback
import xml.etree.ElementTree as ET


"""Function to calculate the layer based on the user height and the layer height"""
def calculate_target_layer(user_height, layer_height):
    return int(user_height / layer_height)

"""Function to find layer height file"""
def get_layer_height(printsetting_file_path):

        with open(printsetting_file_path, 'r') as file:
            xml_string = file.read()
        
        # Parse the XML content
        root = ET.fromstring(xml_string)
        
        # Define the namespace
        namespace = {'ns': 'http://www.autodesk.com/xml/2019/printsetting'}
        
        # Find all parameter_group elements using namespace
        parameter_groups = root.findall('.//ns:parameter_group', namespace)
        
        # Iterate over each parameter_group and each parameter to find layer_height
        for parameter_group in parameter_groups:
            parameters = parameter_group.findall('.//ns:parameter', namespace)
            for parameter in parameters:
                if parameter.get('parameter_id') == 'prm_layer_height':
                    layer_height = float(parameter.get('parameter_real_selected'))
                    print(f"Layer Height found: {layer_height}")
                    return layer_height

if __name__ == "__main__":
    try:
        file_path = r'output\box.gcode'
        get_layer_height(file_path)
    except Exception as e:
        print('Failed:\n{}'.format(traceback.format_exc()))
    
