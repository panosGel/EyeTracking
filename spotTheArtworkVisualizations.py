__author__ = 'panos'
from flask import Flask, session, render_template, request, flash, redirect, url_for, g, jsonify, Markup
from werkzeug import secure_filename
import os
import analysis, plotting
import dataset as ds
import pickle
import uuid
import sqlite3
import fnmatch
from ini import *

# use the analysis to process all our files and create a dataset
# in this example the input files are specified in the array above, as are the times
# we want to use for each file.  The final argument is the path to where the data
# files are stored

#dsStudio = analysis.buildDataSetForStimulus("newDataset",dataFiles,'1934.2med.JPG',inputFilePath)

# next we analyse it - processing into the grid of boxes
#analysis.analyseDataSet(dsStudio)


# if we want to create plots, we need to get the plotter
#plotter = analysis.getPlotter()

# we can now generate a plot of this data set
# ds is the dataset
# 3 plots fixation frequency (see analysis.py for others)
# 0.6 sets the scale of the z-axis
# label is used to specify the plot title
# outfile gives the filename for the plot
#analysis.getGridSize(dsStudio)

#plotter.plotDataSet(dsStudio, 0, 0.6, label="Studio", outfile="heatmap.png")
#plotter.plotFixations(dsStudio.participantList,"studio.png",'1934-2med-jpg.png',)
#plotter.plotPaths(dsStudio, 'studio2.png', image='1934-2med-jpg.png')
# plotter.plotDataSet(dsLocation, 3, 0.6, outfile="location.png")
recordings = os.listdir(GAZE_DATA)
print recordings
imageNames = os.listdir(IMAGE_FOLDER)
print imageNames
# specify the analysis parameters
parameters = {
        'gridWidth': 10,                  # the grid size: set to None for dynamic calcluation
        'gridHeight': None,                # the grid size: set to None for square shaped boxes
        'errorRadius': 10,                 # error smoothing sigma (pixels)
        'groupingRadius': 50,              # filtering radius (pixels)
        'fixationLengthFilter': 100        # minimum fixation length
        }
def createImageDatasets():

    for image in imageNames:
        analysisObject = analysis.Analysis(parameters)
        analysisObject.outputPath = DATASET_FOLDER
        imageDataset = analysisObject.buildDataSetForStimulus(image,recordings,image,GAZE_DATA)
        analysisObject.getGridSize(imageDataset)
        analysisObject.analyseDataSet(imageDataset)
        imageDataset.saveToFile(image)



def visualizeGazePlots():

    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER

    imageDataset = ds.DataSet.loadFromFile(DATASET_FOLDER+"1917.170med_resized.jpg.data")
    imageDataset = analysisOb.buildDataSetForStimulus("1917.170med_resized.jpg",recordings,"1917.170med_resized.jpg",GAZE_DATA)
    analysisOb.getGridSize(imageDataset)
    analysisOb.analyseDataSet(imageDataset)

    plotterOb = analysisOb.getPlotter()
    for participant in imageDataset.participantList:
        plotterOb.plotFixations([participant],VISUALISER_FOLDER+imageNames[0]+"_"+participant.number+"_gazeplot.png",
                                VISUALISER_FOLDER+"1917.170med_resized.png")


    #plotterOb.plotPaths(imageDataset,imageNames[0]+"_pathPlot.png",VISUALISER_FOLDER+"\\"+"1917.170med_resized.png")
    #plotterOb.plotDataSet(imageDataset, 1, 0.6, label="1917.170med_resized.png", outfile="1917.170med_resized_heatmap.png")


def visualizeHeatmaps():

    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER
    imageDataset = ds.DataSet.loadFromFile(DATASET_FOLDER+"1917.170med_resized.jpg.data")
    imageDataset = analysisOb.buildDataSetForStimulus("1917.170med_resized.jpg",recordings,"1917.170med_resized.jpg",GAZE_DATA)
    analysisOb.getGridSize(imageDataset)
    analysisOb.analyseDataSet(imageDataset)
    plotterOb = analysisOb.getPlotter()

    plotterOb.plotFixationHeatmap([imageDataset.participantList[0]],VISUALISER_FOLDER+imageNames[0]+"_"+imageDataset.participantList[0].number+"_fixationCountHeatmap.png",
                                VISUALISER_FOLDER+"1917.170med_resized.png")
    plotterOb.plotDataSet(imageDataset,3,1.6,"beach",VISUALISER_FOLDER+"heatmap",VISUALISER_FOLDER+"1917.170med_resized.png")
#createImageDatasets()
visualizeGazePlots()
visualizeHeatmaps()