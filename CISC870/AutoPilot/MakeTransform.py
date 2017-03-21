M = vtk.vtkMatrix4x4()
M.SetElement(0,3,5)
T = slicer.vtkMRMLTransformNode()
T.SetAndObserveMatrixTransformToParent(M)
slicer.mrmlScene.AddNode(T)

N = slicer.util.getNode('OriginToCOM')
#N.ApplyTransformMatrix(M)