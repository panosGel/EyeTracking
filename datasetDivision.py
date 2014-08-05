__author__ = 'panos'
#-----Spot the artwork-----
#   getting the stats and dividing the datasets
#
from ini import *
import csv
import re
from os import path


file = open(STATS_FOLDER+"demData.tsv")
#dictionary for the paintings
paintingsDict = dict([(1, [CHEVIOT_FARM_1,CHEVIOT_FARM_2,CHEVIOT_FARM_3]), (2, [NOW_FOR_THE_PAINTER_1,NOW_FOR_THE_PAINTER_2,NOW_FOR_THE_PAINTER_3]),
                      (3, [KONIGSTEIN_1,KONIGSTEIN_2,KONIGSTEIN_3]),(4,[WOMAN_AND_SUSPENDED_MAN_1,WOMAN_AND_SUSPENDED_MAN_2,WOMAN_AND_SUSPENDED_MAN_3]),
                      (5,[FOURTEEN_SIX_1964_1,FOURTEEN_SIX_1964_2,FOURTEEN_SIX_1964_3]),(6,[CHEETAH_STAGS_1,CHEETAH_STAGS_2,CHEETAH_STAGS_3]),
                      (7,[FLASK_WALK_1,FLASK_WALK_2,FLASK_WALK_3]),(8,[RELEASE_1,RELEASE_2,RELEASE_3]),(9,[SELF_PORTRAIT_1,SELF_PORTRAIT_2,SELF_PORTRAIT_3]),
                      (10,[WEST_WITH_EVENING_1,WEST_WITH_EVENING_2,WEST_WITH_EVENING_3]),(12,[SIR_GREGORY_1,SIR_GREGORY_2,SIR_GREGORY_3]),
                      (11,[RHYL_SANDS_FAMILIARITY_1,RHYL_SANDS_FAMILIARITY_2,RHYL_SANDS_FAMILIARITY_3])])

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
        else  :
            MALE_PARTICIPANTS.append(recordingFile)

        #add recording to proper age group dataset

        if row[14] == "1":
            AGEGROUP_1_PARTICIPANTS.append(recordingFile)
        elif row[14] == "2":
            AGEGROUP_2_PARTICIPANTS.append(recordingFile)

        elif row[14] == "3":
            AGEGROUP_3_PARTICIPANTS.append(recordingFile)

        elif row[14] == "4":
            AGEGROUP_4_PARTICIPANTS.append(recordingFile)

        else:
            AGEGROUP_5_PARTICIPANTS.append(recordingFile)
        #add recording to proper level of interest group dataset
        if row[16] == "very interested":
            INTEREST_GROUP_1_VERY_INTERESTED.append(recordingFile)
        elif row[16] == "quite interested":
            INTEREST_GROUP_2_QUITE_INTERESTED.append(recordingFile)
        elif row[16] == "moderate interest":
            INTEREST_GROUP_3_MODERATE_INTEREST.append(recordingFile)
        elif row[16] == "not very interested":
            INTEREST_GROUP_4_NOT_VERY_INTERESTED.append(recordingFile)

        #familiarity of each artwork
        #
        for i in range(1,12):
            if row[i] == "1":
                paintingsDict.get(i)[0].append(recordingFile)
            elif row[i] == "2":
                paintingsDict.get(i)[1].append(recordingFile)
            else:
                paintingsDict.get(i)[2].append(recordingFile)



finally:
    file.close()

print "gender"
print len(FEMALE_PARTICIPANTS)
print len(MALE_PARTICIPANTS)
print "age group"
print len(AGEGROUP_1_PARTICIPANTS)
print len(AGEGROUP_2_PARTICIPANTS)
print len(AGEGROUP_3_PARTICIPANTS)
print len(AGEGROUP_4_PARTICIPANTS)
print len(AGEGROUP_5_PARTICIPANTS)
print "interest groups"
print len(INTEREST_GROUP_1_VERY_INTERESTED)
print len(INTEREST_GROUP_2_QUITE_INTERESTED)
print len(INTEREST_GROUP_3_MODERATE_INTEREST)
print len(INTEREST_GROUP_4_NOT_VERY_INTERESTED)
print "cheviot farm familiarity"
print len(CHEVIOT_FARM_1)
print len(CHEVIOT_FARM_2)
print len(CHEVIOT_FARM_3)
print "now for the painter familiarity"
print len(NOW_FOR_THE_PAINTER_1)
print len(NOW_FOR_THE_PAINTER_2)
print len(NOW_FOR_THE_PAINTER_3)