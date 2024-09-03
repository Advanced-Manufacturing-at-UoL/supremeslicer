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

class STLViewer:
    def __init__(self, stl_file):
        self.stl_file = stl_file
        self.marker_actor = None
        self.create_renderer()

    def create_renderer(self):
        colors = vtkNamedColors()

        # Read STL file
        reader = vtkSTLReader()
        reader.SetFileName(self.stl_file)
        reader.Update()

        # Create a mapper
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

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
            print(f"Picked position: {picked_position}")
            self.marker_actor.SetPosition(picked_position)

        self.interactor.GetInteractorStyle().OnLeftButtonDown()  # Call the base class method to ensure default behavior

    def start(self):
        self.interactor.Start()
