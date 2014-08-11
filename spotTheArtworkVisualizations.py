__author__ = 'panos'
from flask import Flask, session, render_template, request, flash, redirect, url_for, g, jsonify, Markup
from werkzeug import secure_filename
import os
import analysis, plotting
import dataset as ds
import math
import pickle
import uuid
import sqlite3
import fnmatch
from ini import *



recordings = os.listdir(GAZE_DATA)
print recordings

imageNames = os.listdir(IMAGE_FOLDER)
print imageNames
# specify the analysis parameters
parameters = {
        'gridWidth': 20,                  # the grid size: set to None for dynamic calcluation
        'gridHeight': None,                # the grid size: set to None for square shaped boxes
        'errorRadius': 10,                 # error smoothing sigma (pixels)
        'groupingRadius': 50,              # filtering radius (pixels)
        'fixationLengthFilter': 100        # minimum fixation length
        }
def createImageDataset(imageName):

    analysisObject = analysis.Analysis(parameters)
    analysisObject.outputPath = DATASET_FOLDER
    imageDataset = analysisObject.buildDataSetForStimulus(imageName,recordings,imageName,GAZE_DATA)
    analysisObject.getGridSize(imageDataset)
    analysisObject.analyseDataSet(imageDataset)
    #imageDataset.saveToFile(image)
    return imageDataset

imageDataset = createImageDataset("1917.170med_resized.jpg")
imageDataset
def visualizeGazePlots(imageName):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER


    plotterOb = analysisOb.getPlotter()
    for participant in imageDataset.participantList:
        pngFile = imageName.replace(".jpg",".png",-3)
        plotterOb.plotFixations([participant],VISUALIZER_FOLDER+imageNames[0]+"_"+participant.number+"_FixationsPlot.png",
                                VISUALIZER_FOLDER+pngFile)
    plotterOb.plotPaths(imageDataset,VISUALIZER_FOLDER+"all_participants_gazePlot",VISUALIZER_FOLDER+pngFile)




def visualizeHeatmaps(imageName):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER

    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.replace(".jpg",".png",-3)
    # 0 => plot fixation counts
    # 1 => fixation duration
    # 2 => mean fixation length
    # 3 => fixation frequency
    # 4 => time to first fixation (currently only gives result for first file in list)
    plotterOb.plotDataSet(imageDataset,0,1.4,"Fixation counts heatmap for " +pngFile,VISUALIZER_FOLDER+pngFile+"fixationCountsHeatmap"+".png",VISUALIZER_FOLDER+pngFile)
    plotterOb.plotDataSet(imageDataset,1,0.4,"Fixation duration heatmap for " +pngFile,VISUALIZER_FOLDER+pngFile+"fixationDurationHeatmap"+".png",VISUALIZER_FOLDER+pngFile)
    plotterOb.plotDataSet(imageDataset,2,0.4,"Mean fixation duration heatmap for " +pngFile,VISUALIZER_FOLDER+pngFile+"MeanFixationLengthHeatmap"+".png",VISUALIZER_FOLDER+pngFile)
    plotterOb.plotDataSet(imageDataset,3,0.15,"Fixation frequency heatmap for " +pngFile,VISUALIZER_FOLDER+pngFile+"fixationFrequencyHeatmap"+".png",VISUALIZER_FOLDER+pngFile)
    plotterOb.plotDataSet(imageDataset,4,0.15,"Time to first fixation heatmap for"+pngFile,VISUALIZER_FOLDER+pngFile+"firstFixationTimeHeatmap"+".png",VISUALIZER_FOLDER+pngFile)

def visualizeHeatmapsByGender(imageName):

    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER

    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.replace(".jpg",".png",-3)
    # 0 => plot fixation counts
    # 1 => fixation duration
    # 2 => mean fixation length
    # 3 => fixation frequency
    # 4 => time to first fixation (currently only gives result for first file in list)


def visualizeParticipantsGazePlots(imageName,ParticipantNumber):
    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER

    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.replace(".jpg",".png",-3)
    plotterOb.plotParticipantPaths(imageDataset,ParticipantNumber,VISUALIZER_FOLDER+ParticipantNumber+"_gazeplot",VISUALIZER_FOLDER+pngFile)


def visualizeArbitraryAOI(imageName):
    analysisOb = analysis.Analysis(parameters)
    analysisOb.datasets = DATASET_FOLDER

    plotterOb = analysisOb.getPlotter()
    pngFile = imageName.replace(".jpg",".png",-3)
    plotterOb.plotArbitraryAOI(VISUALIZER_FOLDER+"_ArbitraryAOI",VISUALIZER_FOLDER+pngFile)


#visualizeGazePlots("1917.170med_resized.jpg")
#visualizeArbitraryAOI("1917.170med_resized.jpg")
visualizeHeatmaps("1917.170med_resized.jpg")

#visualizeParticipantsGazePlots("1917.170med_resized.jpg","andy")
#visualizeParticipantsGazePlots("1917.170med_resized.jpg","P0")
#visualizeParticipantsGazePlots("1917.170med_resized.jpg","P1")
#visualizeParticipantsGazePlots("1917.170med_resized.jpg","P2")
#visualizeParticipantsGazePlots("1917.170med_resized.jpg","P3")
#visualizeParticipantsGazePlots("1917.170med_resized.jpg","P4")
#visualizeParticipantsGazePlots("1917.170med_resized.jpg","P5")
