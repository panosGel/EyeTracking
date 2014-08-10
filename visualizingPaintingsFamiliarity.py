__author__ = 'panos'
from ini import *
import os
import analysis, plotting
import datasetDivision as dsDv

imageNames = os.listdir(IMAGE_FOLDER)
print imageNames
datasets=[]
paintingsDsDict = dsDv.divide_datasets()
imageNamesDict = dict([(imageNames[4],paintingsDsDict.get(1)),(imageNames[5],paintingsDsDict.get(2)),
                        (imageNames[10],paintingsDsDict.get(3)),(imageNames[7],paintingsDsDict.get(4)),
                        (imageNames[6],paintingsDsDict.get(5)),(imageNames[8],paintingsDsDict.get(6)),
                        (imageNames[1],paintingsDsDict.get(7)),(imageNames[11],paintingsDsDict.get(8)),
                        (imageNames[2],paintingsDsDict.get(9)),(imageNames[3],paintingsDsDict.get(10)),
                        (imageNames[0],paintingsDsDict.get(11)),(imageNames[9],paintingsDsDict.get(12))])

parameters = {
        'gridWidth': 20,                  # the grid size: set to None for dynamic calcluation
        'gridHeight': None,                # the grid size: set to None for square shaped boxes
        'errorRadius': 10,                 # error smoothing sigma (pixels)
        'groupingRadius': 50,              # filtering radius (pixels)
        'fixationLengthFilter': 100        # minimum fixation length
        }

def createImageDatasets(imageName):
    analysisOb = analysis.Analysis(parameters)
    analysisOb.outputPath= DATASET_FOLDER
    #add datasets to array for later comparison
    datasets=[]
    for i in range(0,3):
        ds_familiarity = analysisOb.buildDataSetForStimulus(imageName,imageNamesDict.get(imageName)[i],imageName,GAZE_DATA)
        analysisOb.analyseDataSet(ds_familiarity)
        plotterOb = analysisOb.getPlotter()
        datasets.append(ds_familiarity)
        pngFile = imageName.lower().replace(".jpg",".png",-3)
        if not os.path.isdir(VISUALIZER_FOLDER_FAMILIARITY+'\\'+pngFile):
            os.mkdir(VISUALIZER_FOLDER_FAMILIARITY+'\\'+pngFile)

        plotterOb.plotDataSet(ds_familiarity,0,1.4,"Fixation counts heatmap for " +pngFile,
                              VISUALIZER_FOLDER_FAMILIARITY+'\\'+pngFile+'\\'+"fixationCountsHeatmap_familiarity_"+str(i)+".png",
                              VISUALIZER_FOLDER+pngFile)
        plotterOb.plotDataSet(ds_familiarity,1,0.4,"Fixation duration heatmap for " +pngFile,
                              VISUALIZER_FOLDER_FAMILIARITY+'\\'+pngFile+'\\'+"fixationDurationHeatmap_familiarity_"+str(i)+".png",
                              VISUALIZER_FOLDER+pngFile)
        plotterOb.plotDataSet(ds_familiarity,2,0.4,"Mean fixation length heatmap for " +pngFile,
                              VISUALIZER_FOLDER_FAMILIARITY+'\\'+pngFile+'\\'+"MeanFixationLengthHeatmap_familiarity_"+str(i)+".png",
                              VISUALIZER_FOLDER+pngFile)
        plotterOb.plotDataSet(ds_familiarity,3,0.15,"Fixation frequency heatmap for " +pngFile,
                              VISUALIZER_FOLDER_FAMILIARITY+'\\'+pngFile+'\\'+"fixationFrequencyHeatmap_familiarity_"+str(i)+".png",
                              VISUALIZER_FOLDER+pngFile)
        plotterOb.plotDataSet(ds_familiarity,3,0.15,"Time to first fixation heatmap for"+pngFile,
                              VISUALIZER_FOLDER_FAMILIARITY+'\\'+pngFile+'\\'+"firstFixationTimeHeatmap_familiarity_"+str(i)+".png",
                              VISUALIZER_FOLDER+pngFile)
    plotterOb = analysisOb.getPlotter()
    #plotterOb.plotFixationComparison(datasets[0],datasets[1],VISUALIZER_FOLDER_FAMILIARITY+"_Comp1.png")



#for image in imageNames:
#    createImageDatasets(image)

createImageDatasets(imageNames[0])