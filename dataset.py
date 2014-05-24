# tool for analysis of eye-tracking data

__version__ = "0.0"

import numpy
# import cPickle as pickle
# import Gnuplot, Gnuplot.funcutils
# import scipy.stats.stats as st  
import scipy.ndimage as scim
import math
import gc, os, sys, traceback
import json
# import sys
import xml.etree.ElementTree as ET

# ########################
# A trivial class to hold screen size values
class Screen:
    width = 1280
    height = 1024

screen = Screen()

NEW_COL_NAMES =  {
    't': "RecordingTimestamp",
    'x': "GazePointX (MCSpx)",
    'y': "GazePointY (MCSpx)",
    's': "MediaName",
    'p': "ParticipantName",
    'd': "GazeEventDuration"
                }

OLD_COL_NAMES = {
    't': "Timestamp",
    'x': "GazePointX",
    'y': "GazePointY",
    's': "StimuliName",
    'p': "Participant:",
    'd': "FixationDuration"
}

# ########################
# A set of participants looking at the same thing
# - they can be logically grouped as a set
class DataSet:

    def __init__(self, label, params, fileList):
        self.parameters = params
        self.label = label
        self.dataFiles = fileList
        self.targetTimes = None
        self.targetStimulus = None
        self.inputFilePath = ""

        # somewhere to collect all our data
        self.participantList = []
        self.aggregatedData = None
        self.offScreenAgg = None

    # #####
    # load a dataset from file
    @staticmethod
    def loadFromDataFile(fileName):
        savedDataSet = pickle.load( open( fileName, "rb" ) ) 
        return DataSet.restoreFromDict(savedDataSet)

    # #####
    # save this dataset to file
    def saveToDataFile(self, fileName=None):
        if not fileName:
            fileName = self.label + ".data"
        savedDataSet = self.saveToDict()
        pickle.dump( savedDataSet, open( fileName, "wb" ) )

    # #####
    # save this dataset to file
    def saveToFile(self, fileName=None):
        if not fileName:
            fileName = self.label + ".xml"
        savedDataSet = self.saveAsXml()
        tree = ET.ElementTree(savedDataSet)
        tree.write(fileName)

    # #####
    # load a dataset from file
    @staticmethod
    def loadFromFile(fileName):
        tree = ET.parse(fileName)
        savedDataSet = tree.getroot()
        return DataSet.createFromXml(savedDataSet)

    # #####
    # build an XML representation of this dataset
    def saveAsXml(self):
        ds =  ET.Element("dataset")
        ds.set("label", self.label)
        
        params = ET.SubElement(ds, "parameters")
        er = ET.SubElement(params, 'errorRadius')
        er.text = str(self.parameters['errorRadius'])
        gr = ET.SubElement(params, 'groupingRadius')
        gr.text = str(self.parameters['groupingRadius'])
        filterL = ET.SubElement(params, 'fixationLengthFilter')
        filterL.text = str(self.parameters['fixationLengthFilter'])
        gridx = ET.SubElement(params, 'gridWidth')
        gridx.text = str(self.parameters['gridWidth'])
        gridx = ET.SubElement(params, 'gridHeight')
        gridx.text = str(self.parameters['gridHeight'])


        participants = ET.SubElement(ds, 'participants')
        for p in self.participantList:
            participants.append(p.saveAsXml())

        '''aggregated = ET.SubElement(ds, "aggregates")
        if self.offScreenAgg:
            aggOffScreen = self.offScreenAgg.saveAsXml()
            aggOffScreen.set('offscreen', str(True))
            aggregated.append(aggOffScreen)
        if self.aggregatedData:
            for i in range(self.parameters['gridWidth']):
                for j in range(self.parameters['gridHeight']):
                    b = self.aggregatedData[i][j].saveAsXml()
                    b.set('x', str(i))
                    b.set('y', str(j))
                    aggregated.append(b)
        '''           

        # files
        # times
        # ... can be calculated from participants

        # path
        # path = ET.SubElement(ds, "inputPath")
        # path.text = str(self.inputFilePath)
        
        # stimulus
        stimulus = ET.SubElement(ds, "stimulusName")
        stimulus.text = str(self.targetStimulus)

        # self.createVisualiserFiles("/home/andy/")
        
        return ds


    # #####
    # create files for Matthew's visualiser
    # path is the absolute path of the root of the visualiser
    # rel path is the relative path within that for storing the files
    def createVisualiserFiles(self, path, relpath="flask", vid_file="4-News-ch-greece-2.webm", vid_offset=0):

        print "Creating vis files " + path + relpath

        files = []
        # save each participant to json file
        for participant in self.participantList:
             # save to new format for Matthew's visualiser
             filename = self.label + "-" + participant.number.strip()
             files.append(filename)
             file_path = os.path.join(path, relpath, filename + ".json")
             participant.saveAsJson(file_path, vid_offset)

        # create manifest file
        manifest =  [{
            "subtitleFilename": "",
            "tradSubtitleFilename": "",
            "clipName": vid_file,
            "clipNameShort": "Greece",
            "clipLanguage": "English",
            "subtitleOffset": 0.0,
            "trackData": [
                {
                    "treatment": 1,
                    "videoFilename": os.path.join(relpath, vid_file),
                    "files": files
                    }]
            }] 

        all = { "trackDataPath":[relpath],
                "trackVisTypes":["Normal"] ,
                "trackVisTypesShort":["NML"],
                "subtitleControl":["None"],
                "recalibration":{ },
                "manifest":manifest
                }
        
        outFile = open(os.path.join(path, relpath, self.label + "-manifest.json"), 'w')
        outFile.write(json.dumps(all))
        outFile.close()
       

    # #####
    # restore from XML node
    @staticmethod
    def createFromXml(node):
        times = []
        files = []
        participants = []
        plist = node.find('participants')
        ps = plist.findall('participant')
        for p in ps:
            part = Participant.createFromXml(p)
            participants.append(part)
            times.append((part.startTime, part.endTime))
            files.append(part.fileName)

        ps = node.find('parameters')
        params = {}
        params['errorRadius'] = int(ps.find('errorRadius').text)
        params['groupingRadius'] = int(ps.find('groupingRadius').text)
        params['fixationLengthFilter'] = int(ps.find('fixationLengthFilter').text)
        params['gridWidth'] = int(ps.find('gridWidth').text)
        params['gridHeight'] = int(ps.find('gridHeight').text)

        restored = DataSet(node.get('label'), params, files)
        restored.targetTimes = times
        restored.participantList = participants
        # restored.inputFilePath = node.find('inputPath').text
        restored.targetStimulus = node.find('stimulusName').text

        # aggregated data...

        return restored



    # #####
    # read the raw data files, and process them
    def collectData(self, newRecordingFormat=False):

        if newRecordingFormat:
            columnNames = NEW_COL_NAMES
        else:
            columnNames = OLD_COL_NAMES

        filecount = 0
        for inputFile in self.dataFiles:
            fileName = self.inputFilePath + inputFile

            # collect fixation data from file
            recording = Recording(fileName, columnNames=columnNames)
            if len(recording.fixationList) == 0:
                fixations = []
                startTime = 0
                endTime = 0
            elif self.targetStimulus:
                fixations = recording.getFixationsOnStimulus(self.targetStimulus)
                # need to get start and end times for frequency
                startTime = fixations[0].time
                endTime = fixations[-1].time + fixations[-1].duration
            elif self.targetTimes:
                if self.targetTimes[filecount][0] is None:
                    startTime = recording.fixationList[0].time
                else:
                    startTime = self.targetTimes[filecount][0]
                if self.targetTimes[filecount][1] is None:
                    endTime = recording.fixationList[-1].time + recording.fixationList[-1].duration
                else:
                    endTime = self.targetTimes[filecount][1]
                fixations = recording.getFixationsWithinTimes(startTime, endTime)
            else:
                # whole recording
                fixations = recording.getAllFixations()
                startTime = fixations[0].time
                endTime = fixations[-1].time + fixations[-1].duration
            print "Analysing " + fileName + " between " + str(startTime) + " and " + str(endTime)
            participant = Participant(fixations, startTime, endTime)
            participant.fileName = inputFile
            participant.number = recording.participantID.strip()
            self.participantList.append(participant)
            
            participant.filterFixationList(self.parameters['groupingRadius'], self.parameters['fixationLengthFilter'])
            filecount += 1


    # #####
    # apply smoothing to data, then group into boxes
    def smoothAndBoxData(self):
        for participant in self.participantList:
            print "Analysing " + participant.fileName + " between " + str(participant.startTime) + " and " + str(participant.endTime)
            participant.generatePixelData(self.parameters['errorRadius'])
            participant.generateBoxedData(self.parameters['gridWidth'], self.parameters['gridHeight'])
            participant.killPixelData()
            # participant.generatePathData(self.parameters['gridWidth'], self.parameters['gridHeight'])


    # #####
    # generate and return a summary of the data collected
    # returns an array of boxes
    def getAggregateData(self):
        # may have already done this
        # if self.aggregatedData is not None:
        #    return self.aggregatedDat, self.offScreenAgg

        self.aggregatedData = [[] for _ in range(self.parameters['gridWidth'])]
        for i in range(self.parameters['gridWidth']):
            for j in range(self.parameters['gridHeight']):
                # create an array for each variable
                countResults = []
                durationResults = []
                meanDuratioResults = []
                firstFixResults = []
                frequencyResults = []
                # now put a value for each participant in each array
                for participant in self.participantList:
                    pBoxData, offScreenData = participant.getBoxData()
                    pBox = pBoxData[i][j]
                    countResults.append(pBox.count)
                    durationResults.append(pBox.duration)
                    meanDuratioResults.append(pBox.meanDuration)
                    firstFixResults.append(pBox.firstFixTime)
                    frequencyResults.append(pBox.frequency)
                # create a box, and assign arrays to the box
                resultsBox = Box()
                resultsBox.count = countResults
                resultsBox.duration = durationResults
                resultsBox.meanDuration = meanDuratioResults
                resultsBox.firstFixTime = firstFixResults
                resultsBox.frequency = frequencyResults
                # put the box in our data array
                self.aggregatedData[i].append(resultsBox)

        # off screen aggregate
        aggOffScreen = Box()
        aggOffScreen.count = []
        aggOffScreen.duration = []
        aggOffScreen.meanDuration = []
        aggOffScreen.firstFixTime = []
        aggOffScreen.frequency = []
        for p in self.participantList:
            boxes, off = p.getBoxData()
            aggOffScreen.count.append(off.count)
            aggOffScreen.duration.append(off.duration)
            aggOffScreen.meanDuration.append(off.meanDuration)
            aggOffScreen.firstFixTime.append(off.firstFixTime)
            aggOffScreen.frequency.append(off.frequency)
        self.offScreenAgg = aggOffScreen

        return self.aggregatedData, aggOffScreen

    # #####
    # generate and return a summary of one aspect of the data collected
    # returns an array of values
    def getAggregateDataAsArray(self, plot):
        testData = [[] for _ in range(self.parameters['gridWidth'])]
        for i in range(self.parameters['gridWidth']):
            for j in range(self.parameters['gridHeight']):
                # create an array for each variable
                durationResults = []
                # now put a value for each participant in each array
                for participant in self.participantList:
                    pBoxData, pOff = participant.getBoxData()
                    pBox = pBoxData[i][j]
                    durationResults.append(pBox.getResult(plot))
                # create a box, and assign arrays to the box
                # put the box in our data array
                testData[i].append(durationResults)
        return testData
        

    # #####
    # development method - writes unboxed pixel data 
    # into pixels.dat, in gnuplot friendly form    
    def printPixelData(self, pixdata):
        outFile = open("pixels.dat", 'w')
        for i in range(screen.width):
            for j in range(screen.height):
                if pixdata[i][j][0] > 0.01:
                    outFile.write(str(i) + "\t" + str(j) + "\t" + str(pixdata[i][j][0]) + "\n")
        outFile.close()

               
# ###############################################
# A class representing/holding a chunk data from a single data file
class Participant:

    def __init__(self, rawFixationList, startTime, endTime): # , stimulus=""):

        self.startTime = startTime
        self.endTime = endTime
        # self.stimulusId = stimulus
        self.rawFixationList = rawFixationList
        self.fixationList = [] 
        self.pixels = None
        self.boxes = None
        self.offScreen = None
        self.paths = None
        self.gridX = None
        self.gridY = None    
        self.fileName = None
        self.number = "P?"

        
    # #####
    # filter the fixation list, so that those that are close,
    # and sequential are grouped together as a single fixation
    def filterFixationList(self, filterLength, filterTime):
        self.fixationList = Recording.filterFixationList(self.rawFixationList, filterLength, filterTime)
        return self.fixationList


    # #####
    # get an array of data, with fixations spread over pixels according to the
    # error radius
    # populates pixels, a 3D array with count and duration for each pixel
    def generatePixelData(self, filterRadius, speed=1):

        # create a pixel array of unsmoothed pixels
        counts = numpy.zeros((screen.width/speed, screen.height/speed))
        durations = numpy.zeros((screen.width/speed, screen.height/speed))
        for fix in self.fixationList:
            # only on-screen fixations
            if fix.x  >= 0 and fix.y >= 0:
            # print(fix)
                counts[fix.x/speed][fix.y/speed] += 1
                durations[fix.x/speed][fix.y/speed] += fix.duration

        # smooth
        counts = scim.filters.gaussian_filter(counts, filterRadius)
        durations = scim.filters.gaussian_filter(durations, filterRadius)

        # stack and return
        self.pixels = numpy.dstack((counts, durations))
        return self.pixels

    # #####
    # returns the pixel data
    def getPixelData(self):
        return self.pixels

    # #####
    # load the pixel data from file
    def loadPixelData(self, filename):
        self.pixels = pickle.load( open( filename, "rb" ) )
      
    # #####
    # clear the pixel data - saves memory
    def killPixelData(self):
        self.pixels = None
        gc.collect()

    # #####
    # takes the pixel data and chunks it into boxes
    # popluates and returns self.boxes
    def generateBoxedData(self, gridX, gridY, pixelData=None):

        if pixelData is None:
            pixelData = self.pixels

        self.gridX = gridX
        self.gridY = gridY

        # print "\t\t creating empty array"
        # create a 2d array of empty Boxes
        boxes = [[] for _ in range(gridX)]
        for i in range(gridX):
            for j in range(gridY):
                boxes[i].append(Box())
        
        boxWidth = int(screen.width/gridX)+1
        boxHeight = int(screen.height/gridY)+1

        dimensions = numpy.dsplit(pixelData,2)
        counts = dimensions[0]
        durations = dimensions[1]
        i = 0; j = 0
        for col in numpy.array_split(counts, gridY, 1):
            for cell in numpy.array_split(col, gridX, 0):
                boxes[i][j].count =  sum(sum(cell))[0]
                i += 1
            j+=1; i = 0

        i = 0; j = 0
        for col in numpy.array_split(durations, gridY, 1):
            for cell in numpy.array_split(col, gridX, 0):
                boxes[i][j].duration =   sum(sum(cell))[0]
                i += 1
            j+=1; i = 0              

        # now time to first fixation
        # (this doesn't (can't) use smeared data)
        for fix in self.fixationList:
            if fix.x < 0:
                # only look at on-screen fixations for now...
                break
            xBoxId = int(fix.x/boxWidth)
            yBoxId = int(fix.y/boxHeight)
            box = boxes[xBoxId][yBoxId]
            if numpy.isnan(box.firstFixTime):
                box.firstFixTime = fix.time - self.startTime

        # now gather off-screen fixations
        # (this also doesn'tuse smeared data)
        offScreen = Box()
        for fix in self.fixationList:
            if fix.x == -100 and fix.y == -100:
                offScreen.count += 1
                offScreen.duration += fix.duration
                if numpy.isnan(offScreen.firstFixTime):
                    offScreen.firstFixTime = fix.time - self.startTime
        if offScreen.count > 0:
            offScreen.meanDuration = offScreen.duration/offScreen.count
            offScreen.frequency = (1000*offScreen.count)/float(self.endTime - self.startTime)

        # now frequency and mean duration
        for i in range(gridX):
            for j in range(gridY):
                if boxes[i][j].count > 0:
                    boxes[i][j].frequency = (1000*boxes[i][j].count)/float(self.endTime - self.startTime)
                    boxes[i][j].meanDuration = boxes[i][j].duration/boxes[i][j].count
        # print("\t\t ttff and frequency boxing done")

        self.boxes = boxes
        self.offScreen = offScreen
        return self.boxes, offScreen

    # #####
    # get the boxed data
    def getBoxData(self):
        return self.boxes, self.offScreen

    # #####
    # get the data showing fixation movements
    # populates and returns self.paths
    def generatePathData(self, gridX, gridY):
        # print "\t collecting fixation path data"
        numBoxes = gridX * gridY
        paths = numpy.zeros((numBoxes,numBoxes))

        if len(self.fixationList) > 1:
            boxWidth = int(screen.width/gridX)+1
            boxHeight = int(screen.height/gridY)+1

            lastBoxX = self.fixationList[0].x / boxWidth
            lastBoxY = self.fixationList[0].y / boxHeight
        
            for fix in self.fixationList[1:]:
                thisBoxX = fix.x / boxWidth
                thisBoxY = fix.y / boxHeight
                # print str(thisBoxX) + ", " + str(thisBoxY)
                lastBoxIndex = (lastBoxY * gridX) + lastBoxX
                thisBoxIndex = (thisBoxY * gridX) + thisBoxX
                # print str(lastBoxIndex) + " -> " + str(thisBoxIndex)
                paths[lastBoxIndex][thisBoxIndex] += 1
        
                lastBoxX = thisBoxX
                lastBoxY = thisBoxY

        self.paths = paths
        return self.paths


    # #####
    # get the path data
    def getPathData(self):
        return self.paths

    
    # #####
    # save as an XML element
    def saveAsXml(self):
        p = ET.Element("participant")
        p.set("filename", self.fileName)
        p.set("number", str(self.number))

        fixes = ET.SubElement(p, "fixations")
        for fix in self.fixationList:
            fixes.append(fix.saveAsXml())

        rawfixes = ET.SubElement(p, "rawFixations")
        for fix in self.rawFixationList:
            rawfixes.append(fix.saveAsXml())

        boxes = ET.SubElement(p, "boxes")
        if self.boxes:
            for i in range(self.gridX):
                for j in range(self.gridY):
                    b = self.boxes[i][j].saveAsXml()
                    b.set('x', str(i))
                    b.set('y', str(j))
                    boxes.append(b)

        gridsize = ET.SubElement(p, "gridSize")
        if self.gridX:
            gridx = ET.SubElement(gridsize, "width")
            gridx.text = str(self.gridX)
        if self.gridY:
            gridy = ET.SubElement(gridsize, "height")
            gridy.text = str(self.gridY)

        times = ET.SubElement(p, "times")
        t0 = ET.SubElement(times, "start")
        t0.text = str(self.startTime)
        t1 = ET.SubElement(times, "finish")
        t1.text = str(self.endTime)
        
        if self.offScreen:
            os = self.offScreen.saveAsXml()
            os.set('offscreen', str(True))
            boxes.append(os)

        # paths...

        return p

    # #####
    # create a new Participant from an XML element
    @staticmethod
    def createFromXml(node):
        times = node.find('times')
        start = int(times.find('start').text)
        finish = int(times.find('finish').text)
        p = Participant(None, start, finish)
        p.fileName = node.get('filename')
        p.number = node.get('number')

        p.fixationList = []
        fixationlist = node.find('fixations')
        fixations = fixationlist.findall('fixation')
        for fix in fixations:
            p.fixationList.append(Fixation.createFromXml(fix))

        p.rawFixationList = []
        rawFixationsList = node.find('rawFixations')
        rawFixations = rawFixationsList.findall('fixation')
        for rfix in rawFixations:
            p.rawFixationList.append(Fixation.createFromXml(rfix))

        grid = node.find("gridSize")
        w = grid.find("width")
        if w is not None:
            p.gridX = int(w.text)
        h = grid.find("height")
        if h is not None:
            p.gridY = int(h.text)

        boxList = node.find('boxes')
        boxes = boxList.findall('box')
        if len(boxes) > 0:
            # create empty array
            p.boxes = []
            for i in range(p.gridX):
                col = []
                for j in range(p.gridY):
                    col.append(None)
                p.boxes.append(col)

            for b in boxes:
                if b.get('offscreen'):
                    os = Box.createFromXml(b)
                    p.offScreen = os
                else:
                    i = int(b.get('x'))
                    j = int(b.get('y'))
                    p.boxes[i][j] = Box.createFromXml(b)
                    
        # paths...

        return p


    # #####
    # save as a json file in format for Matthew's software to work with
    # contains some hard-coded coordinatefixes
    # offsetTime is the time between start of this dataset and start of video
    # we assume all participants start at same time in the video - this
    # value is the time between the start of the video, and the start of this 
    # dataset
    def saveAsJson(self, filename, videoOffsetTime):
        print "Saving " + filename + " with offset=" + str(videoOffsetTime) 
        # the height of the video as it appeared on screen, in pixels
        # assume video took full width
        videoHeight = 819
        
        segmenttime = float(self.endTime - self.startTime)/1000
        header = { "ParticipantName": self.number.strip(),
                   "RecordingName": self.fileName,
                   "MediaWidth": screen.width,
                   "MediaHeight": videoHeight,
                   "SegmentName": "",
                   "SegmentDuration": segmenttime }
        timestamps = []
        durations = []
        locations = []
        for fix in self.fixationList:
            xpos = float(fix.x)/screen.width
            ypos = float(screen.height-fix.y-(float(screen.height-videoHeight)/2))/videoHeight
            timestamps.append(float(fix.time-self.startTime+videoOffsetTime)/1000)
            durations.append(float(fix.duration)/1000)
            locations.append({"x": xpos, "y": ypos})

        all = { "header": header,
                "RecordingTimestamp": timestamps,
                "GazeEventDuration": durations,
                "FixationPoint": locations
                }
        outFile = open(filename, 'w')
        outFile.write(json.dumps(all))
        outFile.close()
                         
        
# ###############################################
# The fixations from a single data file
class Recording:

    # #####
    # create a recording from a Tobii tsv file
    # columnNames may be used to specify the names of the columns 
    # that the x, y, t, stimulus and participant can be found
    def __init__(self, filename, filepath="", columnNames=None):
        self.filename = filepath + filename
        self.fixationList = []
        self.participantID = ""
        self.columnIndices = None # {'x': 19, 'y': 20, 't': 0, 's': 26, 'd': 34, 'p': 1 }
        if columnNames is None:
            self.columnNames = OLD_COL_NAMES
        else:
            self.columnNames = columnNames

        self.readFile()

    # #####
    # reads all fixations from the file
    def readFile(self):

        f = file(self.filename)

        # try and get column names from each line in turn, until we get them
        while not self.getColumnNumbers(f.readline(), self.columnNames):
            pass
        # print "Got column names: " + str(self.columnIndices)

        # now we can get the data
        for dataline in f:
            # parse data from the file
            try:
                time, x, y, stimulusName, duration = self.parseLine(dataline)
                
                # tobii uses 0,0 as top L: convert to bottom L
                y = screen.height - y

            except ValueError:
                # print "error reading line"
                pass  # line of file isn't fixation data
            else:
                try:
                    # raise exception if x and y out of screen
                    if x < 0 or y < 0:
                        # print "neg coord: " + str(x) + ", " + str(y)
                        raise FixationOutOfBoundsException("Negative coordinate for fixation")
                    if x > screen.width or y > screen.height:
                        # print "big coord: " + str(x) + ", " + str(y)
                        ### what if user can scroll...?
                        raise FixationOutOfBoundsException("Over-large coordinate for fixation")
                    
                    # create a Fixation and add to the list
                    fixation = Fixation(time, x, y, duration, stimulusName)
                    self.fixationList.append(fixation)

                except FixationOutOfBoundsException:
                    pass # fixation not on screen...


    # #####
    # parse a line of the data file
    def parseLine(self, dataline):
        tokens = dataline.split("\t")

        # just get this if we don't have it already
        if self.participantID == "":
            self.participantID = tokens[self.columnIndices['p']].strip()

        time = int(tokens[self.columnIndices['t']])
        x = int(tokens[self.columnIndices['x']])
        y = int(tokens[self.columnIndices['y']])
        stimulusName = tokens[self.columnIndices['s']]
        duration = tokens[self.columnIndices['d']]
        # print str(time) + ":\t" + str(x) + ", " + str(y) + " - " + stimulusName
        return time, x, y, stimulusName, duration


    # #####
    # parse a line of the data file to find the correct column
    # numbers for the data.  Returns true if it finds them, false
    # if an exception is encountered
    # also scans for participant in line, as old style files contained this 
    # in an early line, rather than each column
    def getColumnNumbers(self, dataline, columnNames):
        try:
            # print "Reading line to get column numbers"
            tokens = dataline.split("\t")

            # old style file has list of attributes at top
            # maybe participant name is here
            if tokens[0].strip() == columnNames['p']:
                self.participantID = tokens[1]
                # print "Got pid = " + self.participantID

            self.columnIndices = { 't': tokens.index(columnNames['t']) }
            self.columnIndices['x'] = tokens.index(columnNames['x'])
            self.columnIndices['y'] = tokens.index(columnNames['y'])
            self.columnIndices['s'] = tokens.index(columnNames['s'])
            self.columnIndices['d'] = tokens.index(columnNames['d'])
            # only look for id if we haven't found it in a previous line
            if self.participantID == "":
                self.columnIndices['p'] = tokens.index(columnNames['p'])

            return True
        except:
            # print "Unexpected error:", sys.exc_info()[0]
            # traceback.print_exc(file=sys.stdout)
            return False


    # #####
    # returns a list with a copy of all the fixations in the recording
    def getAllFixations(self):
        sublist = []
        for fix in self.fixationList:
            sublist.append(fix.clone())
        return sublist

    # #####
    # returns a list with a copy of all the fixations within given times
    def getFixationsWithinTimes(self, startTime, endTime):
        sublist = []
        for fix in self.fixationList:
            if fix.time >= startTime and fix.time < endTime:
                sublist.append(fix.clone())
        return sublist

    # #####
    # returns a list with a copy of all the fixations on given stimulus
    def getFixationsOnStimulus(self, stimulus):
        sublist = []
        for fix in self.fixationList:
            if fix.stimulusName == stimulus:
                sublist.append(fix.clone())
        
        return sublist
        
    # #####
    # takes a list and returns a new list with fixations
    # filtered according to a distance and time
    #
    # Time-adjacent fixations within the length will be gathered into
    # a single fixation, which will be added to the list if it is
    # itself longer than the filter time
    @staticmethod
    def filterFixationList(list, filterLength, filterTime):
        # print "\t filtering fixations"
        filteredList = []

        if len(list) == 0:
            return filteredList

        newGroupSize = 1
        newGroup = list[0].clone()
          
        for fix in list[1:]:
            distance = Util.radialDistance(fix.x, fix.y, newGroup.x, newGroup.y)
            if distance < filterLength:
                # yes - add it
                newGroup.x = Util.incrementAverage(newGroup.x, newGroupSize, fix.x)
                newGroup.y = Util.incrementAverage(newGroup.y, newGroupSize, fix.y)
                newGroupSize += 1
            else:
                # no - close group
                newGroup.duration = fix.time - newGroup.time
                # and round coords to integers
                newGroup.x = int(round(newGroup.x))
                newGroup.y = int(round(newGroup.y))
                if newGroup.duration > filterTime:
                    # only include if in filter time, and not off-screen
                    if not (newGroup.x == 0 and newGroup.y == screen.height):
                        filteredList.append(newGroup)
                    else:
                        # would be nice to record these off-screen gaze periods
                        newGroup.x = -100
                        newGroup.y = -100
                        filteredList.append(newGroup)

                # create a new group with this fixation
                newGroup = fix.clone()
                newGroupSize = 1

        # and add final fixation group
        newGroup.duration = fix.time - newGroup.time
        newGroup.x = int(round(newGroup.x))
        newGroup.y = int(round(newGroup.y))
        if newGroup.duration > filterTime and newGroup.isValid():
            # print newGroup
            filteredList.append(newGroup)

        return filteredList


    # #####
    # segment a recording into slices of time, as specified by start, finish and offsets
    # offsets is an array of times for splitting the recording, in ms relative to the start time
    # returns a list of 'Participants', one for each segment
    def generateParticipantsByTime(self, startTime, offsets, finishTime=None):
        if len(self.fixationList) == 0:
            return []

        if finishTime is None:
            # slice all the way to the end of the recording
            finishTime = self.fixationList[:-1].time

        offsets.append(finishTime-startTime)

        # print offsets
        # create a participant per segment, and return them all as a list
        participants = []
        i = 0
        for offset in offsets[:-1]:
            start = startTime + offset
            end = startTime + offsets[i+1]
            print str(start) + " to " + str(end)
            rawFixationList = self.getFixationsWithinTimes(start, end)
            p = Participant(rawFixationList, start, end)
            p.fileName = os.path.basename(self.filename)
            p.number = self.participantID
            # p.startTime = chunk[0]
            # p.endTime = chunk[1]
            participants.append(p)
            i += 1

        return participants


    # #####
    # segment a recording into equal length slices of time, between given 
    # start and end times
    #
    # returns a list of 'Participants', one for each segment
    '''
    def generateParticipantsByTimeSlice(self, startTime, sliceLength, finishTime=None):
        if len(self.fixationList) == 0:
            return []

        if finishTime is None:
            # slice all the way to the end of the recording
            finishTime = self.fixationList[:-1].time
          
        # calculate pairs of start/end times, one per segment
        times = []
        sliceStart = startTime
        sliceEnd = sliceStart + sliceLength
        while sliceEnd < finishTime:
            times.append((sliceStart, sliceEnd))
            sliceStart = sliceEnd
            sliceEnd += sliceLength

        # create a participant per segment, and return them all as a list
        participants = []
        for chunk in times:
            rawFixationList = self.getFixationsWithinTimes(chunk[0], chunk[1])
            p = Participant(rawFixationList, chunk[0], chunk[1])
            p.fileName = os.path.basename(self.filename)
            p.number = self.participantID
            # p.startTime = chunk[0]
            # p.endTime = chunk[1]
            participants.append(p)

        return participants
    '''

# ###############################################
#
class Fixation:

    # create a new fixation
    def __init__(self, time, x, y, duration, stimulusName):
        self.time = time
        self.x = x
        self.y = y
        self.stimulusName = stimulusName
        self.duration = duration

                     
    # #####
    # some fixations have 0,0 coordinate (transformed to 0, 1024)
    # ignore these...
    def isValid(self):
        if self.x == 0 and self.y == screen.height:
            return False
        return True
            
    # #####
    # create a deep copy of this fixation 
    def clone(self):
        copy = Fixation(self.time, self.x, self.y, self.duration, self.stimulusName)
        # print self.time
        return copy
                                    
    # #####
    # save as a tuple, actually a dictionary 
    def saveAsTuple(self):
        t = {
            'time': self.time,
            'x': self.x,
            'y': self.y,
            'duration': self.duration,
            'stimulusName': self.stimulusName
            }
        return t


    # #####
    # returns True if this fixation is within rectangle at (x, y) with width w and height h
    def isOnTarget(self, x, y, w, h):
        return self.x >= x and self.y >= y and self.x <= (x+w) and self.y <= (y+h)


    # #####
    # create a Fixation object from a tuple 
    # assumes dictionary structured as above
    @staticmethod
    def createFromTuple(t):
        f = Fixation(t['time'], t['x'], t['y'], t['duration'], t['stimulusName'])
        return f


    # #####
    # save as an XML element
    def saveAsXml(self):
        fix = ET.Element("fixation")
        x = ET.SubElement(fix, "x")
        x.text = str(self.x)
        y = ET.SubElement(fix, "y")
        y.text = str(self.y)
        t = ET.SubElement(fix, "time")
        t.text = str(self.time)
        d = ET.SubElement(fix, "duration")
        d.text = str(self.duration)
        n = ET.SubElement(fix, "stimulusName")
        n.text = str(self.stimulusName)
        return fix

    # #####
    # create a new Fixation from an XML element
    @staticmethod
    def createFromXml(node):
        t = int(node.find('time').text)
        x = int(node.find('x').text)
        y = int(node.find('y').text)
        d = int(node.find('duration').text)
        n = node.find('stimulusName').text
        return Fixation(t, x, y, d, n)

    # #####
    # toString 
    def __str__(self):
        return str(self.time) + " at (" + str(self.x) + ", " + str(self.y) + ") for " + str(self.duration)
    
       
# ###############################################
# Exception created when we create a Fixation with invalid coordinates
class FixationOutOfBoundsException(Exception):
    pass
   
          
# ###############################################
# A box in a grid that can summarise a region (spacewise) of data
class Box:

    def __init__(self):
        self.count = 0
        self.duration = 0 # total fixation time
        self.meanDuration = numpy.nan
        self.firstFixTime = numpy.nan # time of first fixation
        self.frequency = 0

    # #####
    # get the value for a given plot integer
    # 0 -> count, 1 -> duration, etc.
    def getResult(self, plot):
        if plot == 0:
            return self.count
        elif plot == 1:
            return self.duration
        elif plot == 2:
            return self.meanDuration
        elif plot == 3:
            return self.frequency
        elif plot == 4:
            return self.firstFixTime

    # #####
    # save as an XML element
    def saveAsXml(self):
        box = ET.Element("box")
        c = ET.SubElement(box, "count")
        c.text = str(self.count)
        d = ET.SubElement(box, "duration")
        d.text = str(self.duration)
        md = ET.SubElement(box, "meanDuration")
        md.text = str(self.meanDuration)
        f = ET.SubElement(box, "frequency")
        f.text = str(self.frequency)
        ttff = ET.SubElement(box, "firstFixTime")
        ttff.text = str(self.firstFixTime)
        return box

    # #####
    # create a new Box from an XML element
    @staticmethod
    def createFromXml(node):
        b = Box()
        b.count = float(node.find('count').text)
        b.duration = float(node.find('duration').text)
        b.meanDuration = float(node.find('meanDuration').text)
        b.frequency = float(node.find('frequency').text)
        b.firstFixTime = float(node.find('firstFixTime').text)
        return b

    # #####
    # toString 
    def __str__(self):
        return "count: " + str(self.count) + "; duration: " + str(self.duration) + "; mean duration: " + str(self.meanDuration) + "; frequency: " + str(self.frequency) + "; first fix: " + str(self.firstFixTime)

# ###############################################
# Static utility functions
class Util:

    # #####
    # Given an average, and the number of samples used to get it,
    # returns the new average when another value is added
    @staticmethod
    def incrementAverage(currentAv, currentCount, newValue):
        total = (currentCount * currentAv) + newValue
        count = currentCount + 1
        return float(total)/count

    # #####
    # Calculate the straight line distance between (x,y) and (a,b)
    @staticmethod
    def radialDistance(x, y, a, b):
        dx = x - a
        dy = y - b
        rsq = dx*dx + dy*dy
        return math.sqrt(rsq)


