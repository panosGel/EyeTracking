__author__ = 'panos'
import numpy as np
import matplotlib.pyplot as plt
import datasetDivision as div
from ini import *

#
###Spot the artwork##
#  compute means for fixation count, fixation duration
#  and frequency. We also plot this means along with the
#  standard deviation for all 12 paintings
#

def getBoxStatisticsPlots(meanValues,maxValues,minValues,meanStd,xlabel,ylabel,title):

    N=12

    paintingsMax = [1.83,1.83,1.83,1.83,1.83,1.83,1.83,1.83,1.83,1.83,1.838,1.83]
    paintingsMin = [0.2458,0.2458,0.2458,0.2458,0.2458,0.2458,0.2458,0.2458,0.2458,0.2458,0.2458,0.2458]
    paintingsMeans = [0.702,0.702,0.702,0.702,0.702,0.702,0.702,0.702,0.702,0.702,0.702,0.702]
    paintingsStd = [0.5,0.6,0.7,0.4,0.5,0.3,0.2,0.1,0.4,0.3,0.376,0.24]


    index = np.arange(N)
    margin = 0.05
    width = (2.-4.*margin)/N
    #width = (0.1-0.2*margin)/N
    opacity = 0.3
    fig, ax = plt.subplots()
    xdata = index+margin+(N*width)

    meansBar = plt.bar(index+margin+(1*width), paintingsMeans, width,
                 label="Mean fixation count",
                 alpha=opacity,
                 color='b',yerr=paintingsStd
                 )

    plt.xlabel('Paintings')
    plt.ylabel('Viewers')
    plt.title("Mean fixation count")
    plt.xticks(index+0.5, ('Cheviot \nFarm',"Now for\n the painter","Konigstein","Women and\n suspended man","14.06.1964",
                               "Cheetah and\n two indians",
                               "Flask walk","Release","Self portrait","Evening glows","Rhyl Sands","Sir Gregory"))

    plt.legend()
    #plt.tight_layout()
    plt.show()

getBoxStatisticsPlots(1,1,1,1,1,1,1)