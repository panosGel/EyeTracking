__author__ = 'panos'
from ini import *
import os
import analysis, plotting
import datasetDivision as dsDv

imageNames = os.listdir(IMAGE_FOLDER)
print imageNames
paintingsDsDict = dsDv.divide_datasets()
parameters = {
        'gridWidth': 20,                  # the grid size: set to None for dynamic calcluation
        'gridHeight': None,                # the grid size: set to None for square shaped boxes
        'errorRadius': 10,                 # error smoothing sigma (pixels)
        'groupingRadius': 50,              # filtering radius (pixels)
        'fixationLengthFilter': 100        # minimum fixation length
        }

def createImageDatasets(imageName):
    analysisOb = analysis.Analysis(parameters)
    analysisOb.outputPath(DATASET_FOLDER)
    paintingsDict = dsDv.divide_datasets()
    datasets=[]

