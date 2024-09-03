#!/bin/env python

"""
Simple VTK example in Python to load an STL mesh and display with a manipulator.
Chris Hodapp, 2014-01-28, (c) 2014
"""

import vtk
print(vtk.VTK_MAJOR_VERSION, vtk.VTK_MINOR_VERSION)

def render():
    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    # Create a RenderWindowInteractor to permit manipulating the camera
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    stlFilename = "input/benchy.stl"
    polydata = loadStl(stlFilename)
    ren.AddActor(polyDataToActor(polydata))
    ren.SetBackground(0.1, 0.1, 0.1)
    
    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()

def loadStl(fname):
    """Load the given STL file, and return a vtkPolyData object for it."""
    reader = vtk.vtkSTLReader()
    reader.SetFileName(fname)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata

def polyDataToActor(polydata):
    """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)  # Updated for VTK 6.0+
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    #actor.GetProperty().SetRepresentationToWireframe()
    actor.GetProperty().SetColor(0.5, 0.5, 1.0)
    return actor

render()
