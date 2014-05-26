
import unittest
import analysis as an
import dataset as ds
import cPickle as pickle
import random
import numpy
import sys
import xml.etree.ElementTree as ET

class TestBoxFunctions(unittest.TestCase):

    def setUp(self):
        self.testBox = ds.Box()
        self.testBox.count = 10
        self.testBox.duration = 11
        self.testBox.meanDuration = 12
        self.testBox.frequency = 13
        self.testBox.firstFixTime = 14

    def test_count_output(self):
        self.assertEqual(self.testBox.getResult(0), 10)

    def test_duration_output(self):
        self.assertEqual(self.testBox.getResult(1), 11)

    def test_mean_duration_output(self):
        self.assertEqual(self.testBox.getResult(2), 12)

    def test_frequency_output(self):
        self.assertEqual(self.testBox.getResult(3), 13)

    def test_first_fix_output(self):
        self.assertEqual(self.testBox.getResult(4), 14)


class TestUtilFunctions(unittest.TestCase):

    def test_average_increment(self):
        testArray = [0,1,3,4,5,6,8]
        expected = 3.8571429
        actual = 0;
        counter = 0
        for val in testArray:
            actual = ds.Util.incrementAverage(actual, counter, val)
            counter += 1
        self.assertAlmostEqual(actual, expected)

    def test_radial_distance(self):
        expected = 5
        actual = ds.Util.radialDistance(0, 0, 3, 4)
        self.assertEqual(expected, actual)

    def test_radial_distance_with_negatives(self):
        expected = 10
        actual = ds.Util.radialDistance(-3, -4, 3, 4)
        self.assertEqual(expected, actual)


class TestRecording(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.rec = ds.Recording("gaze_data/Rec 01/Rec 01-All-Data.tsv")
        self.studioList = self.rec.getFixationsWithinTimes(6440, 27449)
        self.filteredList = self.rec.filterFixationList(self.studioList, 50, 100)
        startTime = 6440
        endTime = 27449
        sliceLength = 5000
        
        offsets = []
        end = 0
        while end < (endTime-startTime-sliceLength):
            offsets.append(end)
            end += sliceLength
        end += startTime
            
        self.slicedList = self.rec.generateParticipantsByTime(startTime, offsets, end)            
        # self.slicedList = self.rec.generateParticipantsByTimeSlice(startTime, sliceLength, endTime)

    def test_read_file_gets_all_fixations(self):
        expectedFixCount = 8147 # plus 2 out of bounds
        actualFixCount = len(self.rec.fixationList)
        self.assertEqual(actualFixCount, expectedFixCount)

    def test_recording_sublist_raw(self):
        expectedFixCount = 1054
        actualFixCount = len(self.studioList)
        self.assertEqual(actualFixCount, expectedFixCount)

    def test_filtered_fixation_list_length(self):
        expectedFixCount = 43 # one of which is off-screen
        actualFixCount = len(self.filteredList)
        self.assertEqual(actualFixCount, expectedFixCount)


    # #####
    # test that the time has been sliced correctly
    def test_time_slicing_list_size(self):
        self.assertEqual(len(self.slicedList), 4)

        self.assertEqual(self.slicedList[0].startTime, 6440)
        self.assertEqual(self.slicedList[1].startTime, 11440)
        self.assertEqual(self.slicedList[2].startTime, 16440)
        self.assertEqual(self.slicedList[3].startTime, 21440)
        self.assertEqual(self.slicedList[0].endTime, 11440)
        self.assertEqual(self.slicedList[1].endTime, 16440)
        self.assertEqual(self.slicedList[2].endTime, 21440)
        self.assertEqual(self.slicedList[3].endTime, 26440)


    # #####
    # test that the fixations have been gathered correctly for each time slot
    def test_time_slicing_raw_fixation_counts(self):
        self.assertEqual(len(self.slicedList[0].rawFixationList), 251)
        self.assertEqual(len(self.slicedList[1].rawFixationList), 250)
        self.assertEqual(len(self.slicedList[2].rawFixationList), 251)
        self.assertEqual(len(self.slicedList[3].rawFixationList), 251)

    # #####
    # test that the fixations have been filtered correctly for each time slot
    def test_time_slicing_filtered_fixation_counts(self):
        for p in self.slicedList:
            p.filterFixationList(50, 100)
        
        self.assertEqual(len(self.slicedList[0].fixationList), 13)
        self.assertEqual(len(self.slicedList[1].fixationList), 13)
        self.assertEqual(len(self.slicedList[2].fixationList), 8) # one off screen
        self.assertEqual(len(self.slicedList[3].fixationList), 9)

    # #####
    # test that the fixation attributes are correct at boundaries
    def test_time_slicing_filtered_boundary_attributes(self):
        for p in self.slicedList:
            p.filterFixationList(50, 100)
        
        self.assertEqual(self.slicedList[0].fixationList[-1].time, 11078)
        self.assertEqual(self.slicedList[0].fixationList[-1].duration, 359)
        self.assertEqual(self.slicedList[0].fixationList[-1].x, 928)

        self.assertEqual(self.slicedList[1].fixationList[0].time, 11457)
        self.assertEqual(self.slicedList[1].fixationList[0].duration, 657)
        self.assertEqual(self.slicedList[1].fixationList[0].x, 933)

        self.assertEqual(self.slicedList[3].fixationList[-1].time, 26270)
        self.assertEqual(self.slicedList[3].fixationList[-1].duration, 159)
        self.assertEqual(self.slicedList[3].fixationList[-1].x, 925)

        

class TestParticipant(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.rec = ds.Recording("datafiles/p4.tsv")
        fixList = self.rec.getFixationsWithinTimes(6440, 27449)
        self.p = ds.Participant(fixList, 6440, 27449)#, "")
        self.filteredList = self.p.filterFixationList(50, 100)

    def test_filtered_fixation_list_length(self):
        expectedFixCount = 43 # one off-screen
        actualFixCount = len(self.filteredList)
        self.assertEqual(actualFixCount, expectedFixCount)

    # #####
    # save a participant with fixation list, then restore
    # and test we still have the same number of fixations
    '''def test_participant_pickling(self):
        saved = self.p.saveAsDict()
        restored = ds.Participant.createFromDict(saved)
        self.assertEqual(len(restored.fixationList), 43)
        '''

    # #####
    # save a participant with fixation list, then restore
    # and test we still have the same number of fixations
    def test_participant_xml(self):
        saved = self.p.saveAsXml()
        restored = ds.Participant.createFromXml(saved)
        self.assertEqual(len(restored.fixationList), 43)
    
    # #####
    # give the participant a dummy pixel set, and test they are
    # boxed evenly
    def test_pixel_boxing(self):
        # create a dummy pixel array
        pixels = [[1,2]]*1024
        pixels = numpy.array([pixels]*1280)
        self.p.pixels = pixels
        boxes, offScreen = self.p.generateBoxedData(10, 8)
        totalcount = 0
        totalduration = 0
        for i in boxes:
            for b in i:
                totalcount += b.count
                totalduration += b.duration
                # print(b.count)
                self.assertEqual(b.count, 16384)
                self.assertEqual(b.duration, 16384*2)
            
        self.assertEqual(totalcount, 1280*1024)
        self.assertEqual(totalduration, 1280*1024*2)

    # #####
    # save a participant with fixation list, then restore
    # run pixel smearing on both and compare some
    # random pixels
    def test_participant_xml_with_pixels(self):
        saved = self.p.saveAsXml()
        restored = ds.Participant.createFromXml(saved)
        savePix = self.p.generatePixelData(50)
        restPix = restored.generatePixelData(50)

        # test a random number of pixels
        for x in range(30):
            i = random.randint(0,1279)
            j = random.randint(0,1023)
            self.assertEqual(savePix[i][j][1], restPix[i][j][1])
            
    # #####
    # save a participant with boxes, then recreate
    # and compare a random box
    def test_participant_xml_with_boxes(self):
        self.p.generatePixelData(50)
        self.p.generateBoxedData(10, 8)
        saved = self.p.saveAsXml()
        # ET.dump(saved)
        restored = ds.Participant.createFromXml(saved)
        # test a random number of pixels
        for x in range(10):
            i = random.randint(0,9)
            j = random.randint(0,7)
            savedBox = self.p.boxes[i][j]
            restBox = restored.boxes[i][j]
            self.assertAlmostEqual(savedBox.count, restBox.count)

    # #####
    # save a participant with fixation list, then restore
    # run pixel smearing on both and compare some
    # random pixels
    '''def test_participant_pickling_with_pixels(self):
        saved = self.p.saveAsDict()
        restored = ds.Participant.createFromDict(saved)
        savePix = self.p.generatePixelData(50)
        restPix = restored.generatePixelData(50)

        # test a random number of pixels
        for x in range(30):
            i = random.randint(0,1279)
            j = random.randint(0,1023)
            self.assertEqual(savePix[i][j][1], restPix[i][j][1])
            
    # #####
    # save a participant with boxes, then recreate
    # and compare a random box
    def test_participant_pickling_with_boxes(self):
        self.p.generatePixelData(50)
        self.p.generateBoxedData(10, 8)
        saved = self.p.saveAsDict()
        restored = ds.Participant.createFromDict(saved)
        i = random.randint(0,9)
        j = random.randint(0,7)
        savedBox = self.p.boxes[i][j]
        restBox = restored.boxes[i][j]
        self.assertEqual(savedBox.saveAsTuple(), restBox.saveAsTuple())
        '''

# ####
# test the gross function - ensures consistency, if not correctness
# 
class TestAnalysis(unittest.TestCase):

    # P4 and P6
    # studio
    # 10x8, error=50px, filtering=50px/100ms
    # all attributes calculated for each box...
    @classmethod
    def setUpClass(self):
        analysis = an.Analysis()
        self.dataSet = analysis.buildDataSet("unittest", ["datafiles/p4.tsv", "datafiles/p6.tsv"], [[6440,27449],[4051,25326]])
        analysis.analyseDataSet(self.dataSet)
     
    # ####
    # tests if total duration per box is same as before
    # does not check if this is actually correct!
    def test_compare_current_output(self):
        # run it fresh
        aggregatedData = []
        aggregatedData.append(self.dataSet.getAggregateDataAsArray(0))
        aggregatedData.append(self.dataSet.getAggregateDataAsArray(1))
        aggregatedData.append(self.dataSet.getAggregateDataAsArray(2))
        aggregatedData.append(self.dataSet.getAggregateDataAsArray(3))
        aggregatedData.append(self.dataSet.getAggregateDataAsArray(4))
        # pickle.dump( aggregatedData, open( "unittest-p4p6-agg.data", "wb" ) )
        # print(aggregatedData)

        # load saved version
        savedAggregatedData = pickle.load( open( "unittest-p4p6-agg.data", "rb" ) )
        # compare string representations (as numpy.nan values are objects)
        self.assertEqual(str(aggregatedData[0]), str(savedAggregatedData[0]))
        self.assertEqual(str(aggregatedData[1]), str(savedAggregatedData[1]))
        self.assertEqual(str(aggregatedData[2]), str(savedAggregatedData[2]))
        self.assertEqual(str(aggregatedData[3]), str(savedAggregatedData[3]))
        self.assertEqual(str(aggregatedData[4]), str(savedAggregatedData[4]))


    # #####
    # ensure a dataset is consistent after writing to and reading from 
    # xml file
    def test_dataset_xml_file(self):
        aggCount = self.dataSet.getAggregateDataAsArray(0)
        # xml = self.dataSet.saveAsXml()
        # restored = ds.DataSet.createFromXml(xml)
        self.dataSet.saveToFile('/home/andy/ds.xml')
        restored = ds.DataSet.loadFromFile('/home/andy/ds.xml')
        aggCountSaved = restored.getAggregateDataAsArray(0)
        
        for x in range(50):
            i = random.randint(0,9)
            j = random.randint(0,7)
            self.assertAlmostEqual(aggCount[i][j][1], aggCountSaved[i][j][1])
        
    
if __name__ == '__main__':
    fast = unittest.TestSuite()
    fast.addTest( TestParticipant('test_participant_xml_with_boxes') )
    main = unittest.TestSuite()
    main.addTest( TestAnalysis('test_dataset_xml_file') )
    # unittest.TextTestRunner().run(fast)
    # unittest.TextTestRunner().run(main)
    unittest.main()
