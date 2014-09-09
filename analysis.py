# tool for analysis of eye-tracking data

__version__ = "0.0"

import numpy
import scipy.stats as stats
import scipy.stats.stats as st  
import scipy.ndimage as scim
import math
import gc
import sys
import warnings

import dataset as data
import plotting
import grids
from ini import *
   
# get the screen dimensions from dataset module
# may be better in here, but that requires mutual importing
screen = data.screen

class Analysis:

    # #########################################
    # create a new Analysis, using the given parameters
    # (or the defaults
    def __init__(self, parameters=None):
        if parameters:
            self.params = parameters
        else:
            # Analysis parameters - the defaults
            self.params = {
                'gridWidth': 10,                   # the grid size: set to None for dynamic calcluation
                'gridHeight': None,                # the grid size: set to None for square shaped boxes
                'errorRadius': 10,                 # error smoothing sigma (pixels)
                'groupingRadius': 50,              # filtering radius (pixels)
                'fixationLengthFilter': 100        # minimum fixation length
                }

        # and calculate derived parameter:
        if not self.params['gridHeight']:
            aspectRatio = float(screen.height) / screen.width
            self.params['gridHeight'] = int(aspectRatio * self.params['gridWidth'])

        self.outputPath = "./"

        self.datasets = []

    
    # ########
    # factors involved in finding peaks and determining grid size
    
    # sets what is lower limit for a peak:
    # multiplies mean of all fixations
    # peakLimitFactor = 3

    # minimum separation for two peaks to be considered separate
    # peakSepLimit = 20

    # minumum drop between two peaks so they are considered separate
    # limit determined by mean height of peaks divided by this.
    # peakDropLimitFactor = 2

    # ## Peak separation factor
    # determine grid size from distance between peaks
    # gridSepFactor = 1.7  

    ### what to plot
    # 0 => plot fixation counts
    # 1 => fixation duration
    # 2 => mean fixation length
    # 3 => fixation frequency
    # 4 => time to first fixation (currently only gives result for first file in list)
    plot = 0


    # #####
    # collect a new dataset from the raw fixation data
    def buildDataSet(self, label, dataFiles, timesArray, inputFilePath="", newRecordingFormat=False):
        newDataSet = data.DataSet(label, self.params, dataFiles)
        newDataSet.inputFilePath = inputFilePath
        newDataSet.targetTimes = timesArray
        newDataSet.collectData(newRecordingFormat)
        return newDataSet
       
    # #####
    # collect a new dataset from the raw fixation data
    def loadDataSet(self, filename):
        newDataSet = data.DataSet.loadFromFile(filename)
        return newDataSet
       

    # #####
    # collect a new dataset from the raw fixation data
    def buildDataSetForStimulus(self, label, dataFiles, stimulus, inputFilePath="", newRecordingFormat=False):
        newDataSet = data.DataSet(label, self.params, dataFiles)
        newDataSet.inputFilePath = inputFilePath
        newDataSet.targetStimulus = stimulus
        newDataSet.collectData(newRecordingFormat)
        return newDataSet
       

    # #####
    #  analyse and save a new datasets from the raw fixation data
    def analyseDataSet(self, dataSet):
        dataSet.smoothAndBoxData()
        # save dataset
        dataSet.saveToFile(self.outputPath + dataSet.label + ".data")
        return dataSet

    # #####
    # determine the optimum (?) grid size to apply when boxing a dataset
    def getGridSize(self, dataSet):
        # create a super-participant, with all fixtions from all participants in this dataset
        superParticipant = data.Participant(dataSet.participantList[0].fixationList, None, None)
        for p in dataSet.participantList[1:]:
            superParticipant.fixationList.extend(p.fixationList)

        # now get all fixations as pixel grid
        pix = superParticipant.generatePixelData(self.params['errorRadius'])

        # now do analysis on this grid
        count_array = numpy.dsplit(pix,2)[0]
        gridSep = grids.calculateGridSize(count_array, 3, 100, 5, 1.7)
        print "Grid width should be " + str(screen.width/gridSep) + " boxes"
        return gridSep, (screen.width/gridSep)
    # #####
    # Spot the arwork : create datasets for each time slice, which has
    # a duration of 100ms
    # #####


    # #####
    # split the raw fixation data into time-slices of specified (equal) size, then
    # analyse, etc., and create a new dataset per time slice
    #
    # returns an array of datasets
    def generateTimeSlicedDataSets(self, label, dataFiles, timesArray, sliceLength, inputFilePath=""):

        # generate some offsets, then use the timesplit function

        durations = [(times[1] - times[0])/sliceLength for times in timesArray]
        if(max(durations) != min(durations)):
            raise Exception("Unequal size slices")
        maxLength = max(durations)

        offsets = []
        for i in range(maxLength):
            offsets.append(sliceLength*i)
        
        # adjust end times to match the end of the last slice (all after is ignored)
        for times in timesArray:
            times[1] = times[0]+(maxLength*sliceLength)

        print offsets
        print timesArray

        return self.generateTimeSplitDataSets(label, dataFiles, timesArray, offsets, inputFilePath)

            

    # #####
    # split the raw fixation data into time-slices, as specified by offsets, then
    # analyse, etc., and create a new dataset per time slice
    # offsets are times in ms for each break, specified relative to the start time; 
    # the last value is the (relative) end time of the last slice.
    #
    # returns an array of datasets
    def generateTimeSplitDataSets(self, label, dataFiles, timesArray, offsets, inputFilePath=""):

        # dataFiles and timesArray must be same size
        recordings = []
        for inputFile in dataFiles:
            rec = data.Recording(inputFile, filepath=inputFilePath)
            recordings.append(rec)
            # print("added recording!")

        participantSets = []
        for i in range(len(recordings)):
            r = recordings[i]
            # print(str(timesArray[i][0]) + " to " + str(timesArray[i][1]) + " interval=" + str(sliceLength))
            # clone offsets, as it gets modified for each recording
            slices = r.generateParticipantsByTime(timesArray[i][0], offsets[:], timesArray[i][1])
            # print(str(len(slices)) + " slices from recording " + str(i))
            participantSets.append(slices)
            # now have array of [recording][timeslice]
            
        participantSliceArray = numpy.array(participantSets)

        # filter and box data for each participant
        progress = 1
        for participant in participantSliceArray.flatten():
            print ("analysing chunk " + str(progress) + " of " + str(len(offsets) * len(dataFiles)))
            participant.filterFixationList(self.params['groupingRadius'], self.params['fixationLengthFilter'])
            participant.generatePixelData(self.params['errorRadius'])
            participant.generateBoxedData(self.params['gridWidth'], self.params['gridHeight'])
            participant.killPixelData()
            progress += 1

        # transpose, so each item is list of chunks over same time
        participantSliceArray = participantSliceArray.transpose()
        # now have [timeslice][recording]
        
        # create a dataSet for each time slice
        dataSets = []
        sliceCount = 1
        for timeSlice in participantSliceArray:
            # create data set
            setLabel = label + "-"
            if sliceCount < 10:
                setLabel += "0"
            setLabel += str(sliceCount)# + ": " + str(sliceCount * sliceLength) + "-" + str((sliceCount+1) * sliceLength)
            dset = data.DataSet(setLabel, self.params, dataFiles)
            dset.participantList = timeSlice
            dataSets.append(dset)
            sliceCount += 1

        # and return
        return dataSets

    # #####
    # run the analysis
    def runTimeSlice(self, label, dataFiles, timeSliceTimes, interval, inputFilePath=""):

        self.dataFiles = dataFiles

        """
        self.datasets = self.generateTimeSlicedDataSets(label, self.dataFiles, timeSliceTimes, interval, inputFilePath)
        for dset in self.datasets:
            dset.dataFiles = self.dataFiles
            agg, offScreen = dset.getAggregateData()
            dset.saveToFile(self.outputPath + dset.label + ".data")
            # self.plotDataSet(dset, 3)
        
        """
        for i in range(4)[1:]:
            slicelabel = label + "-"
            if i < 10:
                slicelabel += "0"
            slicelabel = slicelabel + str(i)
            print(slicelabel)
            dset = data.DataSet.loadFromFile(inputFilePath + slicelabel + ".data")
            self.datasets.append(dset)
            agg, offScreen = dset.getAggregateData()
            plotTitle = slicelabel + ": fixation frequency"
            self.plotDataSet(dset, 3, 0.6, label=plotTitle,outfile=self.outputPath+slicelabel+".png")         

        """
        # now look for differences
        i = 0; j = 1
        for setA in self.datasets:
            for setB in self.datasets[i+1:]:
                # self.compareDataSets(setA, setB, 3)
                i += 1
            i = j
            j += 1
        """
                    
            
    # #####
    # run the analysis
    def runComparison(self, dataFiles, inputFilePath, timesA, timesB, labels=("A","B")):
        # self.inputFilePath = inputFilePath        
        # self.dataFiles = dataFiles

        dsA = self.buildDataSet(labels[0], dataFiles, timesA, inputFilePath)
        dsB = self.buildDataSet(labels[1], dataFiles, timesB, inputFilePath)

        # print("getting grid sizes")
        # print self.getGridSize(dsA)
        # print self.getGridSize(dsB)

        self.analyseDataSet(dsA)
        self.analyseDataSet(dsB)

        self.compareDataSets(dsA, dsB, 3, "Fixation frequency")
        self.plotDataSet(dsA, 3)
        self.plotDataSet(dsB, 3)

 
    # #####
    # run the analysis
    def reRunComparison(self, fileA, fileB):
       # from saved
        dsA = data.DataSet.loadFromFile(fileA)
        dsB = data.DataSet.loadFromFile(fileB)

        # normal and pairwise
        self.compareDataSets(dsA, dsB, 3, "Fixation frequency")
        # self.compareDataSets(dsA, dsB, True)


    # ######################################################
    # plotting functions
    # ######################################################


    def getPlotter(self):
        return plotting.Plotter(self.params['gridWidth'], self.params['gridHeight'], self.outputPath)

    # #####
    # compare two datasets on a given value
    # returns boolean, dictionary
    # boolean is true if any box shows difference more significant than sig (default 0.05)
    def generateMplotStats(self, dataSetA, dataSetB, plot, pairwise=False, sig=0.05):
        # catch warnings - eg we may not have enough samples for wilcoxon test
        warnings.filterwarnings("error")
        aggregateDataA, offScreen = dataSetA.getAggregateData()
        aggregateDataB, offScreen = dataSetB.getAggregateData()
        differenceFound = False
        xvalues = []
        yvalues = []
        sizes = []
        pvals = []
        differenceNum=0
        # get x, y magnitude of difference between sets, and significance
        for j in range(self.params['gridHeight']):
            for i in range(self.params['gridWidth']):
                # get two arrays for given plot
                setA = aggregateDataA[i][j].getResult(plot)
                setB = aggregateDataB[i][j].getResult(plot)
                # only compare if mean counts of both are greater than one 
                if st.nanmean(aggregateDataA[i][j].getResult(0)) > 0.5 or st.nanmean(aggregateDataB[i][j].getResult(0)) > 0.5:
                    try:
                        if pairwise:
                            wilcoxon_t, p = stats.wilcoxon(setA, setB)
                        else:
                            mww_z, p = stats.ranksums(setA, setB)
                    except UserWarning:
                        p = 1
                        print("can't do stats on " + str(i) + " " + str(j))

                    xvalues.append(i)
                    yvalues.append(j)
                    # now work out difference to illustrate scale of difference
                    # given as proportion of the bigger number
                    if st.nanmean(setA) > st.nanmean(setB):
                        size = (st.nanmean(setA) - st.nanmean(setB))/st.nanmean(setA)
                        sizes.append(500*size*size)
                        pvals.append(1-p)
                    else:
                        size = (st.nanmean(setB) - st.nanmean(setA))/st.nanmean(setB)
                        sizes.append(500*size*size)
                        pvals.append(p-1)
                    # print str(i) + " " + str(j) + " " + str(p)
                    if p < sig:
                        differenceFound = True
                        differenceNum+=1
           
        return differenceFound, {'x': xvalues, 'y':yvalues, 's':sizes, 'p':pvals} , differenceNum


    # #####
    # generate data in format for spreadsheet to read
    # i.e., a csv file, laid out as table matching boxes
    # one table of means, one of standard deviations
    def writeBoxesToCsvFile(self, dataset, filename, plot):
        boxArray = dataset.getAggregateDataAsArray(plot)
        outFile = open(filename, 'w')
        outFile.write("Means:\n")
        #print("Means:\n")
        for j in reversed(range(self.params['gridHeight'])):
            dataline = ""
            for i in range(self.params['gridWidth']):
                dataline += str(st.nanmean(boxArray[i][j]))
                dataline += ","
            #print dataline
            dataline += "\n"
            outFile.write(dataline)
        
        outFile.write("\nStandardDeviations:\n")
        #print("\nStandardDeviations:\n")
        for j in reversed(range(self.params['gridHeight'])):
            dataline = ""
            for i in range(self.params['gridWidth']):
                dataline += str(numpy.std(boxArray[i][j]))
                dataline += ","
            #print dataline
            dataline += "\n"
            outFile.write(dataline)
 
        outFile.close()


    # #####
    # prints to console a set of values for a given box id over a collection of datasets
    # box id is given as (x,y).
    def printBoxData(self, datasets, boxCoord, plot):
        print "Box " + str(boxCoord)
        means = []
        print "Mean, StdDev, n"
        for ds in datasets:
            alldata = ds.getAggregateDataAsArray(plot)
            boxdata = alldata[boxCoord[0]][boxCoord[1]]
            means.append(st.nanmean(boxdata))
            print str(st.nanmean(boxdata)) + ", " + str(numpy.std(boxdata)) + ", " + str(len(boxdata))
        print "-----"
        print str(st.nanmean(means)) + ", " + str(numpy.std(means)) + ", " + str(len(means))

        for i in range(len(datasets)):
            dsA = datasets[i]
            alldata = dsA.getAggregateDataAsArray(plot)
            boxdata = alldata[boxCoord[0]][boxCoord[1]]
            for j in range(len(datasets))[i+1:]:
                dsB = datasets[j]
                alldataB = dsB.getAggregateDataAsArray(plot)
                boxdataB = alldataB[boxCoord[0]][boxCoord[1]]
                try:
                    mww_z, p = stats.ranksums(boxdata, boxdataB)
                except UserWarning:
                    p = 1

                if p <= 0.05:
                    print "Difference between " + dsA.label + " and " + dsB.label + ".  p = " + str(p)
                else:
                    print "Nothing between " + dsA.label + " and " + dsB.label + "(p=" + str(p) + ")"
                
                
    # #####
    # get a linear array of results for the dataset on the given plot
    # returns an array of tuples: (mean, sd, count)
    def getBoxArray(self, dataset, plot):
        alldata = dataset.getAggregateDataAsArray(plot)
        boxes = []
        for row in alldata:
            for resultArray in row:
            # print box
            # resultArray = box.getResults(plot)
                mean = st.nanmean(resultArray)
                sd = numpy.std(resultArray)
                count = len(resultArray) - numpy.isnan(resultArray).sum()
                boxes.append((mean, sd, count))
        return boxes

    # #####
    # get an array of the values for each participant
    # on the given dataset/plot, for the box with give coords
    # coords supplied as tuple (x,y)
    # returns array of values and tuple of stats (mean, median, sigma)
    def getBoxData(self, dataset, plot, coords):
        alldata = dataset.getAggregateDataAsArray(plot)
        box = alldata[coords[0]][coords[1]]
        mean = st.nanmean(box)
        median = st.nanmedian(box)
        sigma = numpy.std(box)
        return box, (mean, median, sigma)

    # #####
    # get a linear array of comparison for two datasets on the given plot
    # returns an array of tuples: (A, B, p)
    def getCompArray(self, datasetA, datasetB, plot):
        warnings.filterwarnings("error")
        aggregateDataA, offScreen = datasetA.getAggregateData()
        aggregateDataB, offScreen = datasetB.getAggregateData()
        results = []
        # get x, y magnitude of difference between sets, and significance
        for i in range(self.params['gridWidth']):
            for j in range(self.params['gridHeight']):
                # get two arrays for given plot
                setA = aggregateDataA[i][j].getResult(plot)
                setB = aggregateDataB[i][j].getResult(plot)
                # only compare if mean counts of both are greater than one 
                if st.nanmean(aggregateDataA[i][j].getResult(0)) > 1 or st.nanmean(aggregateDataB[i][j].getResult(0)) > 1:
                    # print str(i) + ", " + str(j) + ":  " + str(st.nanmean(setA))
                    try:
                        mww_z, p = stats.ranksums(setA, setB)
                    except UserWarning:
                        p = numpy.nan

                    results.append((st.nanmean(setA), st.nanmean(setB), p))
                else:
                    # print str(i) + ", " + str(j) + ":  " + str(0)
                    results.append((numpy.nan, numpy.nan, numpy.nan))
                    
        return results

