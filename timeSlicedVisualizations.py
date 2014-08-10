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

#array of datasets : each dataset contains a time slice
datasets = []

def createDatasets(imageName):

    analysisObject = analysis.Analysis(parameters)
    analysisObject.outputPath = DATASET_FOLDER
    datasets = analysisObject.generateSlicedDatasets(imageName,recordings,500,GAZE_DATA)

createDatasets(imageNames[0])