__author__ = 'panos'
import os
import analysis, plotting
from ini import *



recordings = os.listdir(GAZE_DATA)

imageNames = os.listdir(IMAGE_FOLDER)
print imageNames

# specify the analysis parameters
parameters = {
        'gridWidth': 21,                  # the grid size: set to None for dynamic calcluation
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

def visualizeFixationCountHeatmap(imageName,imageDataset):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER
    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.replace(".jpg",".png",-3)
    plotterOb.plotDataSet(imageDataset,0,1.7,"Fixation counts heatmap for " +pngFile,VISUALIZER_FOLDER+pngFile+"fixationCountsHeatmap"+".png",VISUALIZER_FOLDER+pngFile)

def visualizeMeanFixationDurationHeatmap(imageName,imageDataset):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.dataFiles = DATASET_FOLDER
    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.replace(".jpg",".png",-3)
    plotterOb.plotDataSet(imageDataset,2,428.0,"Mean fixation duration heatmap for " +pngFile,VISUALIZER_FOLDER+pngFile+"MeanFixationLengthHeatmap"+".png",VISUALIZER_FOLDER+pngFile)


def visualizeFixationFrequencyHeatmap(imageName,imageDataset):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.dataFiles = DATASET_FOLDER
    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.replace(".jpg",".png",-3)
    plotterOb.plotDataSet(imageDataset,3,0.165,"Fixation frequency heatmap for " +pngFile,VISUALIZER_FOLDER+pngFile+"fixationFrequencyHeatmap"+".png",VISUALIZER_FOLDER+pngFile)

def visualizeTimeToFirstFixation(imageName,imageDataset):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.dataFiles = DATASET_FOLDER
    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.replace(".jpg",".png",-3)
    plotterOb.plotDataSet(imageDataset,4,0.15,"Time to first fixation heatmap for"+pngFile,VISUALIZER_FOLDER+pngFile+"firstFixationTimeHeatmap"+".png",VISUALIZER_FOLDER+pngFile)


#fixation heatmaps for all participants

dataset = createImageDataset("1917.170med_resized.jpg",recordings)
visualizeFixationCountHeatmap("1917.170med_resized.jpg",dataset)
visualizeMeanFixationDurationHeatmap("1917.170med_resized.jpg",dataset)
visualizeFixationFrequencyHeatmap("1917.170med_resized.jpg",dataset)
visualizeTimeToFirstFixation("1917.170med_resized.jpg",dataset)