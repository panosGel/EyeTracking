__author__ = 'panos'

__author__ = 'panos'
import os
import analysis, plotting
from ini import *
import random as rnd



recordings = os.listdir(GAZE_DATA)

imageNames = os.listdir(IMAGE_FOLDER)

#default parameters for the analysis object
parameters = {
        'gridWidth': 21,                  # the grid size: set to None for dynamic calcluation
        'gridHeight': None,                # the grid size: set to None for square shaped boxes
        'errorRadius': 5,                 # error smoothing sigma (pixels)
        'groupingRadius': 50,              # filtering radius (pixels)
        'fixationLengthFilter': 100        # minimum fixation length
        }


#compute grid size and create image dataset

def createImageDataset(imageName,eyeTrackingRecordings,datasetLabel):

    analysisObject = analysis.Analysis(parameters)
    analysisObject.outputPath = DATASET_FOLDER
    imageDataset = analysisObject.buildDataSetForStimulus(datasetLabel,eyeTrackingRecordings,imageName,GAZE_DATA)
    gridSize = analysisObject.getGridSize(imageDataset)

    newParameters = {
        'gridWidth': gridSize[1],                  # the grid size: set to None for dynamic calcluation
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

#visualize heatmaps for all participants
#also create a file with min,max, mean values
#for each type of heatmap

def visualizeHeatmaps(imageName,imageDataset):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER

    plotterOb = analysisOb.getPlotter()

    pngFile = imageName.lower().replace(".jpg",".png",-3)
    resultFolder = pngFile.strip(".png") + "\\"
    if not os.path.isdir(VISUALIZER_FOLDER+resultFolder):
        os.mkdir(VISUALIZER_FOLDER+resultFolder)
    resultFile = open(VISUALIZER_FOLDER+resultFolder+pngFile+".txt",'w+')

    # 0 => plot fixation counts
    # 1 => fixation duration
    # 2 => mean fixation length
    # 3 => fixation frequency
    # 4 => time to first fixation (currently only gives result for first file in list)
    outfile = plotterOb.plotDataSet(imageDataset,0,1.7," "
                                    ,VISUALIZER_FOLDER+resultFolder+pngFile+"fixationCountsHeatmap"+".png"
                                    ,VISUALIZER_FOLDER+pngFile)
    #write statistics to .txt file
    resultFile.write("Fixation count results : "+str(outfile[1])+"\n")
    outfile = plotterOb.plotDataSet(imageDataset,2,428.0," "
                                    ,VISUALIZER_FOLDER+resultFolder+pngFile+"MeanFixationLengthHeatmap"+".png"
                                    ,VISUALIZER_FOLDER+pngFile)
    #write statistics to .txt file
    resultFile.write("Fixation mean duration results : "+str(outfile[1])+"\n")
    outfile = plotterOb.plotDataSet(imageDataset,4,0.15," "
                                    ,VISUALIZER_FOLDER+resultFolder+pngFile+"FirstFixationTimeHeatmap"+".png"
                                    ,VISUALIZER_FOLDER+pngFile)
    resultFile.write("Time to first fixation results : "+str(outfile[1])+"\n")

#visualize random gazeplots from all the participants
def visualizeRandomGazeplots(imageName,imageDataset):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.dataFiles = DATASET_FOLDER
    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.lower().replace(".jpg",".png",-3)
    resultFolder = pngFile.strip(".png")
    if not os.path.isdir(VISUALIZER_FOLDER+resultFolder):
        os.mkdir(VISUALIZER_FOLDER+resultFolder)
    sampleSize = len(imageDataset.participantList)
    randomArrayPick =  [rnd.randint(0,66) for i in range(11)]
    for element in randomArrayPick:
        participant = imageDataset.participantList.__getitem__(element)
        num = participant.number
        plotterOb.plotParticipantPaths(imageDataset,num
                                       ,VISUALIZER_FOLDER+resultFolder+'\\'+num+"_gazeplot"
                                       ,VISUALIZER_FOLDER+pngFile)







#paintingsDict = datasetDivision.divide_datasets()

imageDataset = createImageDataset("1934.394med_resized.jpg",recordings,"allParticipants")


visualizeHeatmaps("1934.394med_resized.jpg",imageDataset)
visualizeRandomGazeplots("1934.394med_resized.jpg",imageDataset)
