#!/bin/env python

"""
Simple VTK example in Python to load an STL mesh and display with a manipulator.
Chris Hodapp, 2014-01-28, (c) 2014
"""

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

# Global variables for the renderer and marker actor
ren = None
marker_actor = None

class MyInteractorStyle(vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        super().__init__()
        self.AddObserver('LeftButtonPressEvent', self.onLeftButtonPress)

    def onLeftButtonPress(self, obj, event):
        interactor = obj.GetInteractor()
        click_pos = interactor.GetLastEventPosition()
        print(f"Click position: {click_pos}")

        # Use the global renderer
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)
        picker.Pick(click_pos[0], click_pos[1], 0, ren)
        picked_position = picker.GetPickPosition()

        if picker.GetActor() is not None:
            print(f"Picked position: {picked_position}")
            marker_actor.SetPosition(picked_position)
        
        self.OnLeftButtonDown()  # Call the base class method to ensure default behavior

def render():
    global ren, marker_actor

    colors = vtkNamedColors()

    # Create a rendering window and renderer
    ren = vtkRenderer()
    renWin = vtkRenderWindow()
    renWin.AddRenderer(ren)
    
    # Create a RenderWindowInteractor to permit manipulating the camera
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    # Set up interactor style with custom behavior
    style = MyInteractorStyle()
    iren.SetInteractorStyle(style)
    
    # Load STL file
    stlFilename = "input/benchy.stl"
    polydata = loadStl(stlFilename)
    ren.AddActor(polyDataToActor(polydata))
    ren.SetBackground(colors.GetColor3d('SlateGray'))
    
    # Add a marker actor
    marker_actor = createMarker()
    ren.AddActor(marker_actor)
    
    # Enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()

def loadStl(fname):
    """Load the given STL file, and return a vtkPolyData object for it."""
    reader = vtkSTLReader()
    reader.SetFileName(fname)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata

def polyDataToActor(polydata):
    """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
    mapper = vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.5, 0.5, 1.0)
    return actor

def createMarker():
    """Create a sphere marker."""
    sphereSource = vtkSphereSource()
    sphereSource.SetRadius(0.1)
    sphereSource.SetPhiResolution(20)
    sphereSource.SetThetaResolution(20)
    
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())
    
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Red color
    return actor

if __name__ == '__main__':
    render()
