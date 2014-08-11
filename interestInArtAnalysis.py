__author__ = 'panos'
import os
import analysis, plotting
from ini import *
import datasetDivision



recordings = os.listdir(GAZE_DATA)

imageNames = os.listdir(IMAGE_FOLDER)

paintingsDict = datasetDivision.divide_datasets()
print INTEREST_GROUP_1_VERY_INTERESTED
print INTEREST_GROUP_2_QUITE_INTERESTED
print INTEREST_GROUP_3_MODERATE_INTEREST
print INTEREST_GROUP_4_NOT_VERY_INTERESTED

parameters = {
        'gridWidth': 20,                  # the grid size: set to None for dynamic calcluation
        'gridHeight': None,                # the grid size: set to None for square shaped boxes
        'errorRadius': 10,                 # error smoothing sigma (pixels)
        'groupingRadius': 50,              # filtering radius (pixels)
        'fixationLengthFilter': 100        # minimum fixation length
        }

def createImageDataset(imageName,recordingsSet):

    analysisObject = analysis.Analysis(parameters)
    analysisObject.outputPath = DATASET_FOLDER
    imageDataset = analysisObject.buildDataSetForStimulus(imageName,recordingsSet,imageName,GAZE_DATA)
    print analysisObject.getGridSize(imageDataset)
    analysisObject.analyseDataSet(imageDataset)
    #imageDataset.saveToFile(image)
    return imageDataset

def getBoxDifferences(imageName,dsA,dsB):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER
    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.replace(".jpg",".png",-3)
    fixationCountDifferenceDict = analysisOb.generateMplotStats(dsA,dsB,0)
    fixationMeanDurationDifferenceDict = analysisOb.generateMplotStats(dsA,dsB,2)
    fixationFrequencyDifferenceDict = analysisOb.generateMplotStats(dsA,dsB,3)

    resultArray = [fixationCountDifferenceDict,fixationFrequencyDifferenceDict,fixationMeanDurationDifferenceDict,fixationFrequencyDifferenceDict]

    for element in resultArray:
        print element




ds_1 = createImageDataset("1917.170med_resized.jpg",INTEREST_GROUP_1_VERY_INTERESTED)
ds_2 = createImageDataset("1917.170med_resized.jpg",INTEREST_GROUP_2_QUITE_INTERESTED)
ds_3 = createImageDataset("1917.170med_resized.jpg",INTEREST_GROUP_3_MODERATE_INTEREST)
ds_4 = createImageDataset("1917.170med_resized.jpg",INTEREST_GROUP_4_NOT_VERY_INTERESTED)


print getBoxDifferences("1917.170med_resized.jpg",ds_1,ds_2)
print getBoxDifferences("1917.170med_resized.jpg",ds_1,ds_3)
print getBoxDifferences("1917.170med_resized.jpg",ds_1,ds_4)
print getBoxDifferences("1917.170med_resized.jpg",ds_2,ds_3)
print getBoxDifferences("1917.170med_resized.jpg",ds_2,ds_4)
print getBoxDifferences("1917.170med_resized.jpg",ds_3,ds_4)

