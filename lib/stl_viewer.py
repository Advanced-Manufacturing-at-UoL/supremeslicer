import vtk
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
# Assuming STLViewer is defined in stl_viewer.py

from lib.simulation import SimulationProcessor

class STLViewer:
    """STLViewer class to view Input STL and obtain position of user selected marker"""
    def __init__(self, stl_file, gcode_file, bed_shape, origin=(0, 0, 0), slicer_transform=None):
        self.stl_file = stl_file
        self.origin = self.calculate_origin(bed_shape)
        self.slicer_transform = slicer_transform
        self.marker_actor = None
        self.create_renderer()

        self.gcode = gcode_file
        self.simulator = SimulationProcessor(self.gcode)
        self.center_offsets = self.simulator.get_part_info()

    def calculate_origin(self, bed_shape):
        """Method to calculate origin of the STL"""
        points = []

        for coord in bed_shape.split(','):
            x, y = map(float, coord.split('x'))
            points.append((x, y))
        
        # Calculate the center of the bed
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        return (center_x, center_y, 0)

    def create_renderer(self):
        """Method to create render"""
        colors = vtkNamedColors()

        # Read STL file
        reader = vtkSTLReader()
        reader.SetFileName(self.stl_file)
        reader.Update()

        # Create a transform to adjust the STL origin
        transform = vtk.vtkTransform()
        transform.Translate(self.origin)

        if self.slicer_transform:
            transform.Concatenate(self.slicer_transform)

        # Apply the transform to the STL data
        transform_filter = vtkTransformPolyDataFilter()
        transform_filter.SetTransform(transform)
        transform_filter.SetInputConnection(reader.GetOutputPort())
        transform_filter.Update()

        # Create a mapper
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(transform_filter.GetOutputPort())

        # Create an actor for the STL
        self.actor = vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor(0.5, 0.5, 1.0)  # Set STL color

        # Create a renderer and render window
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(colors.GetColor3d('SlateGray'))
        self.renderer.AddActor(self.actor)
        self.renderer.ResetCamera()

        # Create the marker actor
        self.marker_actor = self.create_marker()
        self.renderer.AddActor(self.marker_actor)

        # Set up the render window and interactor
        self.render_window = vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)

        # Set up interactor style
        self.style = vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(self.style)
        self.style.AddObserver('LeftButtonPressEvent', self.on_left_button_press)

        # Start rendering
        self.render_window.Render()

    def create_marker(self):
        """Method to create a sphere marker."""
        sphere_source = vtkSphereSource()
        sphere_source.SetRadius(0.1)
        sphere_source.SetPhiResolution(20)
        sphere_source.SetThetaResolution(20)

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(sphere_source.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Red color
        return actor

    def on_left_button_press(self, obj, event):
        """Method to handle left button press"""
        click_pos = obj.GetInteractor().GetLastEventPosition()
        print(f"Click position: {click_pos}")

        # Use the global renderer
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)
        picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        picked_position = picker.GetPickPosition()

        # Dynamic Offset calculation
        _offset_x = float(f"{picked_position[0]:.3f}") - self.center_offsets[0]
        _offset_y = float(f"{picked_position[1]:.3f}") -self.center_offsets[1]
        _offset_z = float(f"{picked_position[2]:.3f}") + 1

        _x_pos = float(f"{picked_position[0]:.3f}") - _offset_x
        _y_pos = float(f"{picked_position[1]:.3f}") - _offset_y
        _z_pos = float(f"{picked_position[2]:.3f}") + _offset_z

        if picker.GetActor() is not None:
            print(f"Picked position with dynamic offsets: {_x_pos} {_y_pos} {_z_pos}\n")
            self.marker_actor.SetPosition(picked_position)
            self.selected_point = picked_position

        self.interactor.GetInteractorStyle().OnLeftButtonDown()  # Call the base class method to ensure default behavior

    def start(self):
        """Method to start render"""
        self.interactor.Start()

    def get_selected_point(self):
        """Method for returning selected point"""
        return self.selected_point
