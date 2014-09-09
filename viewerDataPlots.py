__author__ = 'panos'
import numpy as np
import matplotlib.pyplot as plt
import datasetDivision as div
from ini import *


paintingsDictionary = div.divide_datasets()

def gender_plot():

    N = 2
    menNum = (len(MALE_PARTICIPANTS))
    womenNum = (len(FEMALE_PARTICIPANTS))
    index=np.arange(N)

    width = 0.35

    fig,ax = plt.subplots()

    men_rectangle = ax.bar(0, menNum, width, color='r',align='center')
    women_rectangle = ax.bar(width,womenNum,width,color='y',align='center')


    ax.set_ylabel('Viewers')
    ax.set_title('Viewers by gender')
    plt.xticks(index+0.5, ('Male','Female'))
    plt.show()

def agegroups_plot():
    print "age groups"

def interest_plot():
    interest1 = [len(INTEREST_GROUP_1_VERY_INTERESTED)]
    interest2 = [len(INTEREST_GROUP_2_QUITE_INTERESTED)]
    interest3 = [len(INTEREST_GROUP_3_MODERATE_INTEREST)]
    interest4 = [len(INTEREST_GROUP_4_NOT_VERY_INTERESTED)]

    N=1

    index = np.arange(N)
    margin = 0.05
    width = (2.-4.*margin)/N
    #width = (0.1-0.2*margin)/N
    opacity = 0.3
    fig, ax = plt.subplots()
    xdata = index+margin+(N*width)

    int1 = plt.bar(index+margin+(1*width), interest1, width,
                 alpha=opacity,
                 color='b',
                 label="Interest Group 1 : Very interested")
    int2 = plt.bar(index+margin+(2*width), interest2, width,
                 alpha=opacity,
                 color='r',
                 label="Interest Group 2 : Quite interested")
    int3 = plt.bar(index+margin+(3*width), interest3, width,
                 alpha=opacity,
                 color='y',
                 label="Interest Group 3 : Moderate interest")
    int4 = plt.bar(index+margin+(4*width), interest4, width,
                 alpha=opacity,
                 color='g',
                 label="Interest Group 4 :Not very interested")
    plt.xlabel('Interest in art')
    plt.ylabel('Viewers')
    plt.title("Interest of Viewers in art")
    plt.xticks(index+0.5, ('Very\nInterested',"Quite\ninterested","Moderate\nInterest","Not very\nInterested"))

    plt.legend()
    plt.tight_layout()
    plt.show()


def paintingsFamiliarityPlots():
    N = 12


    familiarity1 = [len(paintingsDictionary.get(i)[0]) for i in range (1,13)]
    familiarity2 = [len(paintingsDictionary.get(i)[1]) for i in range (1,13)]
    familiarity3 = [len(paintingsDictionary.get(i)[2]) for i in range (1,13)]
    print familiarity1

    index = np.arange(N)
    margin = 0.05
    width = (2.-4.*margin)/N
    #width = (0.1-0.2*margin)/N
    opacity = 0.3
    fig, ax = plt.subplots()
    xdata = index+margin+(N*width)
    fam1 = plt.bar(index+margin+(1*width), familiarity1, width,
                 alpha=opacity,
                 color='b',
                 label="Familiarity Group 1 : I don\'t recall ever seeing this artwork before")
    plt.text
    fam2 = plt.bar(index+margin+(2*width),familiarity2,width,
                 alpha=opacity,
                 color='r',
                 label="Familiarity Group 2 : I have seen this artwork once or twice before")
    fam3 = plt.bar(index+margin+(3*width),familiarity3,width,
                 alpha=opacity,
                 color='y',
                 label="Familiarity Group 3 : I have seen this artwork many times before")


    plt.xlabel('Paintings')
    plt.ylabel('Viewers')
    plt.title("Familiarity with painting")
    plt.xticks(index+0.5, ('Cheviot \nFarm',"Now for\n the painter","Konigstein","Women and\n suspended man","14.06.1964",
                               "Cheetah and\n two indians",
                               "Flask walk","Release","Self portrait","Evening glows","Rhyl Sands","Sir Gregory"))

    plt.legend()
    plt.tight_layout()
    plt.show()


gender_plot()
