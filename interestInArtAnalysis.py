__author__ = 'panos'
import os
import analysis, plotting
from ini import *
import datasetDivision



recordings = os.listdir(GAZE_DATA)

imageNames = os.listdir(IMAGE_FOLDER)
gridsize=0
paintingsDict = datasetDivision.divide_datasets()

parameters = {
        'gridWidth': 21,                  # the grid size: set to None for dynamic calcluation
        'gridHeight': None,                # the grid size: set to None for square shaped boxes
        'errorRadius': 5,                 # error smoothing sigma (pixels)
        'groupingRadius': 50,              # filtering radius (pixels)
        'fixationLengthFilter': 100        # minimum fixation length
        }

def createImageDataset(imageName,eyeTrackingRecordings,datasetLabel):

    analysisObject = analysis.Analysis(parameters)
    analysisObject.outputPath = DATASET_FOLDER
    imageDataset = analysisObject.buildDataSetForStimulus(datasetLabel,eyeTrackingRecordings,imageName,GAZE_DATA)

    newParameters = {
        'gridWidth': 21,                  # the grid size: set to None for dynamic calcluation
        'gridHeight': None,                # the grid size: set to None for square shaped boxes
        'errorRadius': 5,                 # error smoothing sigma (pixels)
        'groupingRadius': 50,              # filtering radius (pixels)
        'fixationLengthFilter': 100        # minimum fixation length
    }

    analysisObject = analysis.Analysis(newParameters)
    #analysisObject.outputPath = DATASET_FOLDER
    imageDataset = analysisObject.buildDataSetForStimulus(datasetLabel,eyeTrackingRecordings,imageName,GAZE_DATA)
    analysisObject.analyseDataSet(imageDataset)
    return imageDataset

#visualize differences between two datasets
#also write differences into a .txt file
def getBoxDifferences(imageName,dsA,dsB,compDatasets):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER
    plotterOb = analysisOb.getPlotter()

    pngFile = imageName.lower().replace(".jpg",".png",-3)
    resultFolder = pngFile.strip(".png") + "\\" + "interestInArtAnalysis" + "\\"
    if not os.path.isdir(VISUALIZER_FOLDER+resultFolder):
        os.mkdir(VISUALIZER_FOLDER+resultFolder)

    fixationCountDifferenceDict = analysisOb.generateMplotStats(dsA,dsB,0)
    fixationMeanDurationDifferenceDict = analysisOb.generateMplotStats(dsA,dsB,2)
    resultFile = open(VISUALIZER_FOLDER+resultFolder+pngFile+".txt",'a')
    resultFile.write("Fixation counts difference results for groups : "+compDatasets+str(fixationCountDifferenceDict)+"\n")
    resultFile.write("Fixation length difference results : "+compDatasets+str(fixationMeanDurationDifferenceDict)+"\n")
    resultFile.close()
    plotterOb.plotComparisonStats(fixationCountDifferenceDict[1],0,compDatasets,
                                  VISUALIZER_FOLDER+pngFile,VISUALIZER_FOLDER+resultFolder+compDatasets+"_fixCountDiff.png")
    plotterOb.plotComparisonStats(fixationMeanDurationDifferenceDict[1],0,compDatasets,
                                  VISUALIZER_FOLDER+pngFile,VISUALIZER_FOLDER+resultFolder+compDatasets+"_fixMeanDurationDiff.png")

def visualizeHeatmaps(imageName,imageDataset,group):
    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER
    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.lower().replace(".jpg",".png",-3)
    resultFolder = pngFile.strip(".png") + "\\" + "interestInArtAnalysis" + "\\"
    if not os.path.isdir(VISUALIZER_FOLDER+resultFolder):
        os.mkdir(VISUALIZER_FOLDER+resultFolder)
    plotterOb.plotDataSet(imageDataset,0,1.7," ",
                          VISUALIZER_FOLDER+resultFolder+"_fixationCountsHeatmap_"+group +".png",VISUALIZER_FOLDER+pngFile)
    plotterOb.plotDataSet(imageDataset,2,428.0," ",
                          VISUALIZER_FOLDER+resultFolder+"_MeanFixationLengthHeatmap_"+group +".png",VISUALIZER_FOLDER+pngFile)
    plotterOb.plotDataSet(imageDataset,4,0.15," ",
                          VISUALIZER_FOLDER+resultFolder+"_firstFixationTimeHeatmap_"+group +".png",VISUALIZER_FOLDER+pngFile)


ds_1 = createImageDataset("1917.170med_resized.jpg",INTEREST_GROUP_1_VERY_INTERESTED,"interestGroup1")
ds_2 = createImageDataset("1917.170med_resized.jpg",INTEREST_GROUP_2_QUITE_INTERESTED,"interestGroup2")
ds_3 = createImageDataset("1917.170med_resized.jpg",INTEREST_GROUP_3_MODERATE_INTEREST,"interestGroup3")
ds_4 = createImageDataset("1917.170med_resized.jpg",INTEREST_GROUP_4_NOT_VERY_INTERESTED,"interestGroup4")

getBoxDifferences("1917.170med_resized.jpg",ds_1,ds_2,"groups1_2")
getBoxDifferences("1917.170med_resized.jpg",ds_1,ds_3,"groups1_3")
getBoxDifferences("1917.170med_resized.jpg",ds_1,ds_4,"groups1_4")
getBoxDifferences("1917.170med_resized.jpg",ds_2,ds_3,"groups2_3")
getBoxDifferences("1917.170med_resized.jpg",ds_2,ds_4,"groups2_4")
getBoxDifferences("1917.170med_resized.jpg",ds_3,ds_4,"groups3_4")




