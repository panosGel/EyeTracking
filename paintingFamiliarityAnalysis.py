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
        'gridWidth': 21,                  # the grid size: set to None for dynamic calcluation
        'gridHeight': None,                # the grid size: set to None for square shaped boxes
        'errorRadius': 5,                 # error smoothing sigma (pixels)
        'groupingRadius': 50,              # filtering radius (pixels)
        'fixationLengthFilter': 100        # minimum fixation length
        }

def visualizeFamiliarityResults(imageName,parameters):
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
        resultFolder = pngFile.strip(".png")
        famResultFolder = VISUALIZER_FOLDER+resultFolder+"\\"+"familiarityAnalysis"+"\\"
        if not os.path.isdir(famResultFolder):
            os.mkdir(famResultFolder)

        plotterOb.plotDataSet(ds_familiarity,0,1.4,"Fixation counts heatmap for " +pngFile,
                              famResultFolder+"fixationCountsHeatmap_familiarity_"+str(i)+".png",
                              VISUALIZER_FOLDER+pngFile)
        plotterOb.plotDataSet(ds_familiarity,2,0.4,"Mean fixation length heatmap for " +pngFile,
                              famResultFolder+"MeanFixationLengthHeatmap_familiarity_"+str(i)+".png",
                              VISUALIZER_FOLDER+pngFile)

        plotterOb.plotDataSet(ds_familiarity,3,0.15,"Time to first fixation heatmap for"+pngFile,
                              famResultFolder+"firstFixationTimeHeatmap_familiarity_"+str(i)+".png",
                              VISUALIZER_FOLDER+pngFile)
        plotterOb.plotPaths(ds_familiarity,famResultFolder+"gazepath_familiarity_"+str(i)+".png"
                            ,VISUALIZER_FOLDER+pngFile)


    fixationCountDiff_1_2 = analysisOb.generateMplotStats(datasets[0],datasets[1],0)
    fixationMeanDurationDiff_1_2 = analysisOb.generateMplotStats(datasets[0],datasets[1],2)
    resultFile = open(VISUALIZER_FOLDER+resultFolder+pngFile+".txt",'a')
    resultFile.write("Fixation counts difference results for groups : "+compDatasets+str(fixationCountDifferenceDict)+"\n")
    resultFile.write("Fixation length difference results : "+compDatasets+str(fixationMeanDurationDifferenceDict)+"\n")
    resultFile.close()

    plotterOb.plotComparisonStats(fixationCountDiff_1_2[1],0,"Groups 1 & 2",VISUALIZER_FOLDER+pngFile,
                                  famResultFolder+"fixCountDiff_1_2.png")
    plotterOb.plotComparisonStats(fixationMeanDurationDiff_1_2[1],0,"Groups 1 & 2",VISUALIZER_FOLDER+pngFile,
                                  famResultFolder+"fixMeanDur_1_2.png")


    fixationCountDiff_1_3 = analysisOb.generateMplotStats(datasets[0],datasets[2],0)
    fixationMeanDurationDiff_1_3 = analysisOb.generateMplotStats(datasets[0],datasets[2],2)
    plotterOb.plotComparisonStats(fixationCountDiff_1_3[1],0,"Groups 1 & 3",VISUALIZER_FOLDER+pngFile,
                                  famResultFolder+"fixCountDiff_1_3.png")
    plotterOb.plotComparisonStats(fixationMeanDurationDiff_1_3[1],0,"Groups 1 & 3",VISUALIZER_FOLDER+pngFile,
                                  famResultFolder+"fixMeanDur_1_3.png")

    fixationCountDiff_2_3 = analysisOb.generateMplotStats(datasets[1],datasets[2],0)
    fixationMeanDurationDiff_2_3 = analysisOb.generateMplotStats(datasets[1],datasets[2],2)
    plotterOb.plotComparisonStats(fixationCountDiff_2_3[1],0,"Groups 2 & 3",VISUALIZER_FOLDER+pngFile,
                                  famResultFolder+"fixCountDiff_2_3.png")
    plotterOb.plotComparisonStats(fixationMeanDurationDiff_2_3[1],0,"Groups 2 & 3",VISUALIZER_FOLDER+pngFile,
                                  famResultFolder+"fixMeanDur_2_3.png")



#for image in imageNames:
#    createImageDatasets(image)

visualizeFamiliarityResults("1934.394med_resized.jpg",parameters)