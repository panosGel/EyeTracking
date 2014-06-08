__author__ = 'panos'
from flask import Flask, session, render_template, request, flash, redirect, url_for, g, jsonify, Markup
from werkzeug import secure_filename
import os
import analysis, plotting
import dataset as ds
import uuid
import sqlite3
import fnmatch




# path to our data files
inputFilePath = "gaze_data\\"
dataFiles = os.listdir(inputFilePath)
print dataFiles
# list of data file names
# dataFiles = ['Rec 01-All-Data.tsv','Rec 02-All-Data.tsv']

# start and end times for each file, for time slicing
timeSliceTimes = [[14287, 168036], [6440, 156440],[4051,154051],[4273,154273],[3803,153803],[3857,153857],
                  [4071,154071],[3576,153576],[3843,153843],[4911,154911]]

# I was interested in comparing how much people looked at the ticker (at the bottom of the screen)
# when the TV showed a presenter in the studio vs. showing location footage, so I created a
# data set for each.

# times for each file when programme is on location
locationTargetTimes = [[34198,55000], [27449,48000],[25326,46000],[25280,46000],[24945,45000],[24857,45000],
                       [25245,46000],[24614,45000],[25069,46000],[25946,47000]]

# times for each file when programme is in the studio
studioTargetTimes = [[14287,34198], [6440,27449],[4051,25326],[4273,25280],[3803,24945],[3857,24857],
                     [4071,25245],[3576,24614],[3843,25069],[4911,25946]]


# specify the analysis parameters
parameters = {
    'gridWidth': 20,                   # the grid size: set to None for dynamic calcluation
    'gridHeight': None,                # the grid size: set to None for square shaped boxes
    'errorRadius': 10,                 # error smoothing sigma (pixels)
    'groupingRadius': 50,              # filtering radius (pixels)
    'fixationLengthFilter': 100        # minimum fixation length
    }

# Now create an analysis, which will use the parameters above
# note that these are actually the defaults, so we don't have to specify them here
analysis = analysis.Analysis(parameters)

# optionally we can specify where the analysis functions save datasets, etc
# analysis.outputPath = "/home/andy/working/python/"

# use the analysis to process all our files and create a dataset
# in this example the input files are specified in the array above, as are the times
# we want to use for each file.  The final argument is the path to where the data
# files are stored
#dsStudio = analysis.buildDataSet("news-studio-example", dataFiles, studioTargetTimes, inputFilePath)
dsStudio = analysis.buildDataSetForStimulus("newDataset",dataFiles,'1934.2med.JPG',inputFilePath)

# this dataset is now saved as news-studio-example.data and can be loaded with analysis.loadDataSet("news-studio-example.data")

# next we analyse it - processing into the grid of boxes
analysis.analyseDataSet(dsStudio)

# we can create another set for the location data
# dsLocation = analysis.buildDataSet("news-location", dataFiles, locationTargetTimes, inputFilePath)
# analysis.analyseDataSet(dsLocation)

# another option is to slice the data, creating one dataset for each slice
# in this example we slice into 6000ms slices.  The start/finish times for
# each data file (=participant) are given in the array.

# analysis.runTimeSlice("6s-slice", dataFiles, timeSliceTimes, 6000, inputFilePath)

# if we want to create plots, we need to get the plotter
plotter = analysis.getPlotter()

# we can now generate a plot of this data set
# ds is the dataset
# 3 plots fixation frequency (see analysis.py for others)
# 0.6 sets the scale of the z-axis
# label is used to specify the plot title
# outfile gives the filename for the plot
analysis.getGridSize(dsStudio)
plotter.plotDataSet(dsStudio, 3, 0.6, label="Studio", outfile="studio.png")
# plotter.plotDataSet(dsLocation, 3, 0.6, outfile="location.png")