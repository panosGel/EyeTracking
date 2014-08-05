DATASET_FOLDER = 'C:\\Users\\panos\\PycharmProjects\\eyeTracking\\eyeTracking\\datasets\\'
IMAGE_FOLDER = 'C:\\Users\\panos\\PycharmProjects\\eyeTracking\\eyeTracking\\imageFolder'
ALLOWED_EXTENSIONS = set(['tsv', 'xml'])
DATABASE = 'C:\\Users\\panos\\PycharmProjects\\eyeTracking\\eyeTracking\\database\\flask.db'
VISUALIZER_FOLDER = 'C:\\Users\\panos\\PycharmProjects\\eyeTracking\\eyeTracking\\visualizerFolder\\'
GAZE_DATA = "C:\\Users\\panos\\PycharmProjects\\eyeTracking\\eyeTracking\\gazeData\\"
STATS_FOLDER = "C:\\Users\\panos\\PycharmProjects\\eyeTracking\\eyeTracking\\viewerStatistics\\"

PARTICIPANTS_FOLDER = 'C:\\Users\\panos\\PycharmProjects\eyeTracking\eyeTracking\\visualizerFolder\\participantsVisualizations\\'
#separated datasets depending on gender
FEMALE_PARTICIPANTS = []
MALE_PARTICIPANTS = []

#separated datasets depending on agegroup
AGEGROUP_1_PARTICIPANTS = ['Rec 17-All-Data.tsv','Rec 18-All-Data.tsv','Rec 37-All-Data.tsv','Rec 48-All-Data.tsv']
AGEGROUP_2_PARTICIPANTS = ['Rec 02-All-Data.tsv','Rec 14-All-Data.tsv','Rec 47-All-Data.tsv','Rec 52-All-Data.tsv',
                           'Rec 60-All-Data.tsv','Rec 64-All-Data.tsv','Rec 65-All-Data.tsv','Rec 71-All-Data.tsv']
AGEGROUP_3_PARTICIPANTS = ['Rec 03-All-Data.tsv','Rec 10-All-Data.tsv','Rec 21-All-Data.tsv','Rec 23-All-Data.tsv',
                           'Rec 25-All-Data.tsv','Rec 27-All-Data.tsv','Rec 29-All-Data.tsv','Rec 31-All-Data.tsv',
                           'Rec 43-All-Data.tsv','Rec 55-All-Data.tsv','Rec 61-All-Data.tsv','Rec 67-All-Data.tsv',
                           'Rec 70-All-Data.tsv']
AGEGROUP_4_PARTICIPANTS = ['Rec 04-All-Data.tsv','Rec 05-All-Data.tsv','Rec 07-All-Data.tsv','Rec 08-All-Data.tsv',
                           'Rec 11-All-Data.tsv','Rec 13-All-Data.tsv','Rec 20-All-Data.tsv','Rec 22-All-Data.tsv',
                           'Rec 24-All-Data.tsv','Rec 32-All-Data.tsv','Rec 39-All-Data.tsv','Rec 50-All-Data.tsv',
                           'Rec 57-All-Data.tsv',]
AGEGROUP_5_PARTICIPANTS = ['Rec 06-All-Data.tsv','Rec 09-All-Data.tsv','Rec 12-All-Data.tsv','Rec 15-All-Data.tsv',
                           'Rec 16-All-Data.tsv','Rec 19-All-Data.tsv','Rec 26-All-Data.tsv','Rec 30-All-Data.tsv',
                           'Rec 33-All-Data.tsv','Rec 34-All-Data.tsv','Rec 35-All-Data.tsv','Rec 36-All-Data.tsv',
                           'Rec 38-All-Data.tsv','Rec 41-All-Data.tsv','Rec 42-All-Data.tsv','Rec 44-All-Data.tsv',
                           'Rec 45-All-Data.tsv','Rec 46-All-Data.tsv','Rec 51-All-Data.tsv','Rec 53-All-Data.tsv',
                           'Rec 54-All-Data.tsv','Rec 56-All-Data.tsv','Rec 58-All-Data.tsv','Rec 59-All-Data.tsv',
                           'Rec 62-All-Data.tsv','Rec 63-All-Data.tsv','Rec 66-All-Data.tsv','Rec 68-All-Data.tsv',
                           'Rec 69-All-Data.tsv']

#separated datasets depending on level of interest
INTEREST_GROUP_1_VERY_INTERESTED = ['Rec 05-All-Data.tsv','Rec 06-All-Data.tsv','Rec 07-All-Data.tsv','Rec 10-All-Data.tsv',
                                    'Rec 11-All-Data.tsv','Rec 12-All-Data.tsv','Rec 13-All-Data.tsv','Rec 14-All-Data.tsv',
                                    'Rec 16-All-Data.tsv','Rec 19-All-Data.tsv','Rec 22-All-Data.tsv','Rec 24-All-Data.tsv',
                                    'Rec 25-All-Data.tsv','Rec 26-All-Data.tsv','Rec 27-All-Data.tsv','Rec 34-All-Data.tsv',
                                    'Rec 36-All-Data.tsv','Rec 39-All-Data.tsv','Rec 41-All-Data.tsv','Rec 43-All-Data.tsv',
                                    'Rec 47-All-Data.tsv','Rec 51-All-Data.tsv','Rec 54-All-Data.tsv','Rec 62-All-Data.tsv',
                                    'Rec 65-All-Data.tsv']
INTEREST_GROUP_2_QUITE_INTERESTED = ['Rec 02-All-Data.tsv','Rec 03-All-Data.tsv','Rec 04-All-Data.tsv','Rec 08-All-Data.tsv',
                                     'Rec 09-All-Data.tsv','Rec 15-All-Data.tsv','Rec 17-All-Data.tsv','Rec 18-All-Data.tsv',
                                     'Rec 20-All-Data.tsv','Rec 21-All-Data.tsv','Rec 23-All-Data.tsv','Rec 30-All-Data.tsv',
                                     'Rec 31-All-Data.tsv','Rec 32-All-Data.tsv','Rec 33-All-Data.tsv','Rec 37-All-Data.tsv',
                                     'Rec 38-All-Data.tsv','Rec 56-All-Data.tsv','Rec 60-All-Data.tsv','Rec 63-All-Data.tsv',
                                     'Rec 68-All-Data.tsv','Rec 70-All-Data.tsv','Rec 71-All-Data.tsv']
INTEREST_GROUP_3_MODERATE_INTEREST = ['Rec 29-All-Data.tsv','Rec 33-All-Data.tsv','Rec 53-All-Data.tsv','Rec 57-All-Data.tsv',
                                      'Rec 58-All-Data.tsv','Rec 69-All-Data.tsv',]
INTEREST_GROUP_4_NOT_VERY_INTERESTED = ['Rec 42-All-Data.tsv','Rec 46-All-Data.tsv','Rec 48-All-Data.tsv','Rec 50-All-Data.tsv',
                                        'Rec 52-All-Data.tsv','Rec 59-All-Data.tsv','Rec 64-All-Data.tsv','Rec 66-All-Data.tsv',
                                        'Rec 67-All-Data.tsv']



#"rhyl sands" depending on familiarity
RHYL_SANDS_FAMILIARITY_1 = ["ME"]
RHYL_SANDS_FAMILIARITY_2 = []
RHYL_SANDS_FAMILIARITY_3 = []

#"Cheviot farm" datasets depending on familiarity


#"'Now for the Painter' (Rope) - Passengers Going on Board " datasets depending on familiarity


#"The Fortress of Konigstein: Courtyard with the Brunnenhaus" datasets depending on familiarity


#