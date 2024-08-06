import re

class GCodeParser:
    def __init__(self):
        self.current_system = None
        self.polymer_moves = []
        self.ceramic_moves = []
        self.current_position = {'X': 0, 'Y': 0, 'Z': 0, 'A': 0, 'B': 0, 'F': 0}
        self.move_history = []
        self.current_layer = 0
        self.layer_z_values = {}
        self.debug_log = []

    def parse_file(self, filename):
        with open(filename, 'r') as file:
            for line_number, line in enumerate(file, 1):
                self.parse_line(line.strip(), line_number)

    def parse_line(self, line, line_number):
        self.debug_log.append(f"Line {line_number}: {line}")

        if line.startswith(';Layer'):
            match = re.search(r';Layer (\d+) of', line)
            if match:
                self.current_layer = int(match.group(1))
                self.debug_log.append(f"Layer change detected: {self.current_layer}")
        elif 'Z' in line and (line.startswith('G0') or line.startswith('G1')):
            # Extract Z value
            z_match = re.search(r'Z([-\d.]+)', line)
            if z_match:
                z_value = float(z_match.group(1))
                self.layer_z_values[self.current_layer] = z_value
                self.debug_log.append(f"Z value {z_value} set for layer {self.current_layer}")

        if line.startswith('G55'):
            self.current_system = 'polymer'
            self.debug_log.append("Switched to polymer system")
        elif line.startswith('G58'):
            self.current_system = 'ceramic'
            self.debug_log.append("Switched to ceramic system")
        elif self.current_system and line.startswith('G1'):
            self.parse_move(line, line_number)

    def parse_move(self, line, line_number):
        parts = line.split()
        move = self.current_position.copy()
        move['system'] = self.current_system
        move['layer'] = self.current_layer
        
        has_extrusion = False
        for part in parts[1:]:
            if part[0] in 'XYZABF':
                move[part[0]] = float(part[1:])
                if part[0] in 'AB':
                    has_extrusion = True
        
        move['type'] = 'print' if has_extrusion else 'travel'
        
        # Ensure Z value is set for the layer
        if 'Z' not in move and self.current_layer in self.layer_z_values:
            move['Z'] = self.layer_z_values[self.current_layer]
        
        if self.current_system == 'polymer':
            self.polymer_moves.append(move)
        elif self.current_system == 'ceramic':
            self.ceramic_moves.append(move)
        
        self.current_position = {k: v for k, v in move.items() if k not in ['type', 'system', 'layer']}
        self.move_history.append(move)
        
        self.debug_log.append(f"Move parsed: {move}")
    def get_moves(self):
        return self.moves
    
    def get_polymer_moves(self):
        return self.polymer_moves

    def get_ceramic_moves(self):
        return self.ceramic_moves

    def get_move_history(self):
        return self.move_history

    def print_move_summary(self):
        polymer_travel = sum(1 for move in self.polymer_moves if move['type'] == 'travel')
        polymer_print = sum(1 for move in self.polymer_moves if move['type'] == 'print')
        ceramic_travel = sum(1 for move in self.ceramic_moves if move['type'] == 'travel')
        ceramic_print = sum(1 for move in self.ceramic_moves if move['type'] == 'print')

        print("Polymer moves:")
        print(f"  Travel: {polymer_travel}")
        print(f"  Print:  {polymer_print}")
        print("Ceramic moves:")
        print(f"  Travel: {ceramic_travel}")
        print(f"  Print:  {ceramic_print}")

        polymer_layers = set(move['layer'] for move in self.polymer_moves)
        ceramic_layers = set(move['layer'] for move in self.ceramic_moves)
        print(f"Polymer layers: {sorted(polymer_layers)}")
        print(f"Ceramic layers: {sorted(ceramic_layers)}")

    def get_plot_data(self):
        plot_data = {
            'X': [], 'Y': [], 'Z': [], 'A': [], 'B': [], 'F': [],
            'type': [], 'system': [], 'layer': []
        }
        for move in self.move_history:
            for key in plot_data:
                if key in move:
                    plot_data[key].append(move[key])
                else:
                    plot_data[key].append(None)  # For missing values
        return plot_data

    def print_debug_log(self):
        for log in self.debug_log:
            print(log)

# Usage example
if __name__ == "__main__":
    parser = GCodeParser()
    parser.parse_file(r'C:\Users\prali\Desktop\Pralish\Emplyment Work\University Work\Software\CustomSuperSlicer\supremeslicer\output\benchy.gcode')
    moves = parser.get_moves()
    
    print(f"Total moves parsed: {len(moves)}")
    print("First 5 moves:")
    for move in moves[:5]:
        print(move)