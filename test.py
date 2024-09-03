import numpy as np
import vtk

class STLViewer:
    def __init__(self, stl_file, print_space):
        self.stl_file = stl_file
        self.print_space = print_space
        self.transform = vtk.vtkTransform()
        self.actor = None
        self.create_renderer()

    def create_renderer(self):
        # Read STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(self.stl_file)
        reader.Update()

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        # Create an actor
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)

        # Apply initial transformation
        self.actor.SetUserTransform(self.transform)

        # Create a renderer and render window
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(1.0, 1.0, 1.0)  # White background
        self.renderer.AddActor(self.actor)
        self.renderer.ResetCamera()

        # Set up the render window and interactor
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)

        # Set up interactor style
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)

        # Set up keyboard callbacks
        self.interactor.AddObserver("KeyPressEvent", self.on_key_press)

    def on_key_press(self, obj, event):
        key = self.interactor.GetKeySym()

        # Set translation step
        step = 1.0

        # Translation based on key press
        if key == "Left":
            self.transform.Translate(-step, 0, 0)
        elif key == "Right":
            self.transform.Translate(step, 0, 0)
        elif key == "Up":
            self.transform.Translate(0, step, 0)
        elif key == "Down":
            self.transform.Translate(0, -step, 0)
        elif key == "z":
            self.transform.Translate(0, 0, step)
        elif key == "x":
            self.transform.Translate(0, 0, -step)

        self.actor.SetUserTransform(self.transform)
        self.render_window.Render()

    def start(self):
        self.render_window.Render()
        self.interactor.Start()


if __name__ == "__main__":
    # Define the print space (e.g., from Prusa config, in mm)
    print_space = {
        "x": 250,  # mm
        "y": 210,  # mm
        "z": 210   # mm
    }

    # Path to the STL file
    stl_file = "input/benchy.stl"

    # Create and start the viewer
    viewer = STLViewer(stl_file, print_space)
    viewer.start()
