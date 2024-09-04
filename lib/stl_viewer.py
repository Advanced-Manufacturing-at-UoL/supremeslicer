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

class STLViewer:
    def __init__(self, stl_file, bed_shape, origin=(0, 0, 0), slicer_transform=None):
        self.stl_file = stl_file
        self.origin = self.calculate_origin(bed_shape)
        self.slicer_transform = slicer_transform
        self.marker_actor = None
        self.create_renderer()

    def calculate_origin(self, bed_shape):
        # Extract the coordinates from the bed_shape string
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
        colors = vtkNamedColors()

        # Read STL file
        reader = vtkSTLReader()
        reader.SetFileName(self.stl_file)
        reader.Update()

        # Create a transform to adjust the STL origin
        transform = vtk.vtkTransform()

        # Apply origin translation
        transform.Translate(self.origin)

        # Apply any slicer-specific transformation (e.g., rotations, additional translations)
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
        """Create a sphere marker."""
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
        click_pos = obj.GetInteractor().GetLastEventPosition()
        print(f"Click position: {click_pos}")

        # Use the global renderer
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)
        picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        picked_position = picker.GetPickPosition()

        if picker.GetActor() is not None:
            print(f"Picked position: {picked_position:.3f}\n")
            self.marker_actor.SetPosition(picked_position)
            self.selected_point = picked_position

        self.interactor.GetInteractorStyle().OnLeftButtonDown()  # Call the base class method to ensure default behavior

    def start(self):
        self.interactor.Start()

    def get_selected_point(self):
        return self.selected_point