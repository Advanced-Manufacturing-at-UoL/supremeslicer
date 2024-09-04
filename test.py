from tools.vacuum_pnp import VacuumPnP

def test_find_closest_line():
    pnp = VacuumPnP('output/benchy.gcode', 'tools/vacuum_config.yaml')
    pnp.read_gcode()
    pnp.generate_gcode()
    index = pnp._find_closest_line(10, 20, 30)
    print(f"Closest line index: {index}")

test_find_closest_line()
