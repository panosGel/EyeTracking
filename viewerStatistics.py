__author__ = 'panos'
#-----Spot the artwork-----
#   getting the stats and dividing the datasets
#
from ini import *
import csv
import re
from os import path


file = open(STATS_FOLDER+"demData.tsv")
fem_part = []
male_part = []
try:
    reader = csv.reader(file,delimiter='\t')
    for row in reader:

        #get the recording file
        participantNum = row[0]
        recordingNum = participantNum[:-1]
        recordingFile = 'Rec ' + recordingNum + '-All-Data.tsv'

        #add recording to proper gender dataset
        if row[13] == "Female":
            FEMALE_PARTICIPANTS.append(recordingFile)
        elif row[13] == "Male" :
            MALE_PARTICIPANTS.append(recordingFile)


finally:
    file.close()

