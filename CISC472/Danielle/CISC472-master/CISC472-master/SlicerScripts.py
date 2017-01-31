def toggle():
    createModelsLogic = slicer.modules.createmodels.logic()
    
    preModelNode = createModelsLogic.CreateCoordinate(20,2)
    preModelNode.SetName('PreModel')
    preModelNode.GetDisplayNode().SetColor(1,1,0)
    
    originModelNode = createModelsLogic.CreateCoordinate(20,2)
    originModelNode.SetName('OriginModel')
    originModelNode.GetDisplayNode().SetColor(0,1,0)
    
    preModelToRas = slicer.vtkMRMLLinearTransformNode()
    preModelToRas.SetName('PreModelToRas')
    slicer.mrmlScene.AddNode(preModelToRas)  
    preModelToRasTransform = vtk.vtkTransform()
    preModelToRasTransform.PreMultiply() 
    preModelToRasTransform.Translate(0, 0, 50)
    preModelToRasTransform.Update()
    preModelToRas.SetAndObserveTransformToParent(preModelToRasTransform)
    preModelNode.SetAndObserveTransformNodeID(preModelToRas.GetID())
    
    print('button clicked')

b = qt.QPushButton('Click me')
b.connect('clicked()', toggle)
b.show()
