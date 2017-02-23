import vtkSegmentationCorePython as Seg
import csv
Logic = slicer.modules.segmentcomparison.logic()
#OutputDir = 'C:\Users\church\Documents\Winter2017\MICCAI2017\Data'
OutputDir = 'C:\Users\Ben\Documents\Masters16_17\Winter2017\MICCAI2017\Data'
if slicer.util.getNode('SegmentCompare'):
  slicer.mrmlScene.RemoveNode(slicer.util.getNode('SegmentCompare'))

Registrations = slicer.util.getNode('Registrations')
Patients = slicer.util.getNode('Patients')

SC = slicer.vtkMRMLSegmentComparisonNode()
SC.SetName('SegmentCompare')
SC.AddNodeReferenceID('compareSegmentationRef', Patients.GetID())
SC.AddNodeReferenceID('referenceSegmentationRef', Registrations.GetID())
slicer.mrmlScene.AddNode(SC)

with open(OutputDir + '\Metrics.csv', 'wb') as OutputFile:
  OutputWriter = csv.writer(OutputFile)
  OutputWriter.writerow(['Patient #', 'Avg Hausdorff (mm)', 'Max Hausdorff (mm)'])
  SumAvgHaus = 0
  SumMaxHaus = 0
  for i in range(Registrations.GetSegmentation().GetNumberOfSegments()):
    SC.SetReferenceSegmentID(Registrations.GetSegmentation().GetNthSegmentID(i))
    SC.SetCompareSegmentID(Patients.GetSegmentation().GetNthSegmentID(i))
    Logic.ComputeHausdorffDistances(SC)
    #Logic.ComputeDiceStatistics(SC)
    SumAvgHaus += SC.GetAverageHausdorffDistanceForBoundaryMm()
    SumMaxHaus += SC.GetMaximumHausdorffDistanceForBoundaryMm()
    OutputWriter.writerow([Patients.GetSegmentation().GetNthSegment(i).GetName(), SC.GetAverageHausdorffDistanceForBoundaryMm(), SC.GetMaximumHausdorffDistanceForBoundaryMm()])
  AvgAvgHaus = SumAvgHaus / (float(Registrations.GetSegmentation().GetNumberOfSegments()))
  AvgMaxHaus = SumMaxHaus / (float(Registrations.GetSegmentation().GetNumberOfSegments()))
  OutputWriter.writerow(['Avg:', AvgAvgHaus, AvgMaxHaus])
  StdDevAvgHaus = 0
  StdDevMaxHaus = 0
  for i in range(Registrations.GetSegmentation().GetNumberOfSegments()):
    SC.SetReferenceSegmentID(Registrations.GetSegmentation().GetNthSegmentID(i))
    SC.SetCompareSegmentID(Patients.GetSegmentation().GetNthSegmentID(i))
    Logic.ComputeHausdorffDistances(SC)
    StdDevAvgHaus += ((SC.GetAverageHausdorffDistanceForBoundaryMm() - AvgAvgHaus) ** 2) / float((Registrations.GetSegmentation().GetNumberOfSegments()))
    StdDevMaxHaus += ((SC.GetMaximumHausdorffDistanceForBoundaryMm() - AvgMaxHaus) ** 2) / float((Registrations.GetSegmentation().GetNumberOfSegments()))
  OutputWriter.writerow(['StdDev (mm^2)', StdDevAvgHaus, StdDevMaxHaus])
