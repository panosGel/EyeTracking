import numpy
import numpy.ma as ma
from dataset import Util

# #####
# calculate the pixel value of the lowest point between (x,y) and (a,b)
def dropBetween(pixels, x, y, a, b):
    distance = Util.radialDistance(x, y, a, b)
    distance = int(distance/2)

    minVal = pixels[x][y]
    
    for i in range(1, distance):
        pixX = (a-x)/(i*distance)
        pixY = (b-y)/(i*distance)
        pixVal = pixels[int(pixX)][int(pixY)]
        if pixVal < minVal:
            minVal = pixVal

    return minVal

# #####
# get a list of peaks in the given array of pixels
def findPeaks(data, limitFactor):
    mean = sum(sum(sum(data)))/(1280*1024)
    peaks = []
    d = 200
    q = d/2
    for y in xrange(0, data.shape[1], q):
        res = data[:,y:y+d]
        for x in xrange(0, data.shape[0], q):
            cell = res[x:x+d:]
            subMax = numpy.unravel_index(numpy.argmax(cell), (len(cell),len(cell[0])))
            # print cell
            if cell[subMax[0]][subMax[1]] > limitFactor*mean:
                fullx = subMax[0] + x
                fully = subMax[1] + y
            # if not on edge of box
                if subMax[0] != 0 and subMax[0] != d-1 and subMax[1] != 0 and subMax[1] != d-1:
                    peaks.append((fullx, fully))
    return peaks


def filterPeakList(pixels, peaks, separationDist, dropFactor):    
    numPeaks = len(peaks)

    # now filter the list
    tolose = []
    for i in range(numPeaks):
        for j in range(i+1, numPeaks):
            dropLower = False

            # don't keep both if too close
            posi = (peaks[i][0], peaks[i][1])
            posj = (peaks[j][0], peaks[j][1])
            if Util.radialDistance(posi[0], posi[1], posj[0], posj[1]) < separationDist:
                dropLower = True
                   
            # don't keep both if not significant drop
            mean = (pixels[posi[0]][posi[1]] + pixels[posj[0]][posj[1]])/dropFactor
            saddle = dropBetween(pixels, posi[0], posi[1], posj[0], posj[1])
            if(saddle > mean*1):
                dropLower = True

            # if we don't keep both, lose the lower one
            if dropLower:
                if pixels[posi[0]][posi[1]] > pixels[posj[0]][posj[1]]:
                    tolose.append(j)
                else:
                    tolose.append(i)
                
    returnedPeaks = []
    for i in range(numPeaks):
        if i not in tolose:
            returnedPeaks.append(peaks[i])

    # print returnedPeaks
    return returnedPeaks


def calculateGridSize(pixels, lowerLimit, sepDist, dropFact, gridFactor):
    print("Calculating grid size...")
    peaks = findPeaks(pixels, lowerLimit)
    # print("filtering " + str(len(peaks)) + " peaks")
    peaks = filterPeakList(pixels, peaks, sepDist, dropFact)
    # print(str(len(peaks)) + " peaks remaining; calculating grid size")
    minDist = 1280
    numPeaks = len(peaks)
    # print numPeaks
    for i in range(numPeaks):
        for j in range(i+1, numPeaks):
            posi = (peaks[i][0], peaks[i][1])
            posj = (peaks[j][0], peaks[j][1])
            dist = Util.radialDistance(posi[0], posi[1], posj[0], posj[1])
            # print(posi, posj, dist)
            if dist < minDist:
                minDist = dist

    print "Minimum distance is " + str(minDist)
    gridSep = int(minDist/gridFactor)
    return gridSep

"""
import dataset as ds

print("Loading data")

fixList = []
rec = ds.Recording("p4.tsv")
fixList.extend(rec.getFixationsWithinTimes(6440, 27449))

p = ds.Participant(fixList, 6440, 27449)

filteredList = p.filterFixationList(50, 100)

pix = p.generatePixelData(50)

dimensions = numpy.dsplit(pix,2)
data = dimensions[0]
gridSize = calculateGridSize(data, 3, 20, 2, 1.7)
print gridSize
print("use " + str(int(1280/gridSize)) + " x " + str(int(1024/gridSize)) + " grid")
"""
