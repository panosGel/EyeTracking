from matplotlib.patches import Ellipse
import numpy
import scipy.stats.stats as st
import scipy.stats as stats
import matplotlib

matplotlib.use('Agg')

# colormap for stats plots
stats_colormap = {'green':  ((0.0, 0.0, 0.0),
                     (0.25,0.0, 0.0),
                     (0.5, 0.8, 1.0),
                     (0.75,1.0, 1.0),
                     (1.0, 0.4, 1.0)),

          'red': ((0.0, 0.0, 0.0),
                  (0.25,0.0, 0.0),
                  (0.5, 0.8, 0.8),
                  (0.75,0.0, 0.0),
                  (1.0, 0.0, 0.0)),

          'blue':  ((0.0, 0.0, 0.4),
                    (0.25,1.0, 1.0),
                    (0.5, 1.0, 0.8),
                    (0.75,0.0, 0.0),
                    (1.0, 0.0, 0.0)),

          'alpha': ((0.0, 1.0, 1.0),
                    #(0.4, 0.2, 0.2),
                    (0.5, 0.3, 0.3),
                    #(0.6, 0.2, 0.2),
                    (1.0, 1.0, 1.0))
          }


from pylab import *

    # ######################################################
    # plotting functions
    # ######################################################

class Plotter:

    def __init__(self, gridx, gridy, outputPath):
        self.gridx = gridx
        self.gridy = gridy
        self.outputPath = outputPath


    # #####
    # graph results using gnuplot
    # returns the full path to the image file
    def plotDataSet(self, ds, plot, zmax=0.6, label=None, outfile=None, image=None):
        if not outfile:
             outfile = self.outputPath + ds.label + ".png"
             if not label:
                 label = ds.label

        aggregateData, offScreen = ds.getAggregateData()
        # print offScreen
        plotData = self.generatePlotArray(aggregateData, plot, len(ds.dataFiles))

        self.writePlot(plotData, label, zmax, outfile, image)
        return outfile


    # #####
    # generate data in format for matplotlib to read,
    # i.e, a numpy array
    def generatePlotArray(self, boxArray, plot, sampleSize):
        resultArray = numpy.empty((self.gridy, self.gridx))
        #Spot the artwork : changed from nan to zeros
        resultArray[:] = numpy.nan
        for i in range(self.gridx):
            for j in range(self.gridy):
                box = boxArray[i][j]
                count = box.count
                try:
                    count = sum(count)
                except:
                    print "count exception"
                    pass
                if count > sampleSize/4:  # only plot if averaged at least one fixation per participant
                    z = st.nanmean(box.getResult(plot))
                    resultArray[j][i] = z
        return resultArray

    # #####
    # create a plot using matplotlib
    # expects data as [[x,y,val], [x,y,val],...]
    def writePlot(self, myData, plot_title, zMax, fileName, image=None):
        print "Plotting to " + fileName

        figure()

        #if image is None:
        #    image = "/home/andy/wel/Analysis-Tool/4-news.png"

        if image is not None:
            try:
                im = imread(image)
                imshow(im, alpha=0.5, extent=[-0.5,self.gridx-.5,-0.5,self.gridy-.5])
            except IOError:
                print "no image " + image

        imshow(myData, interpolation='spline36', alpha=0.7)
        colorbar(shrink=0.8,aspect=10) # adds scale for colour map, shrunk slightly
        grid(True)
        title(plot_title) # adds title

        ylim(-0.5, self.gridy-0.5) # set axis limits - puts plot right way up
        xlim(-0.5, self.gridx-.5)
        #Spot the artwork - change zMax to the maximum quantity in the data
        clim(0,numpy.nanmax(myData))
        #clim(0, zMax) # set color range scale

        # draw a rectangle for the bbc image
        #picture_base = ( (152.0/1024) * self.gridy ) - 0.5
        #picture_top = ( (872.0/1024) * self.gridy ) - 0.5
        #axhspan(picture_base, picture_top, facecolor='0.5', alpha=0.3) # draw a rectangle on the plot

        ax = axes() # now hide the axis scales
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        # ax.set_aspect('equal', 'datalim')
        # save to file
        savefig(fileName)


    # #####
    # plot the stats comparison using matplotlib
    # plots circle per box:
    #    size represents significance of difference
    #    shading represents magnitude of difference
    #    also plots small and large red circles on points where p < 0.1 and p < 0.05
    #
    # stats in form: {'x': x coords, 'y': y coords: 's' size, 'p': pval }
    # size represents size and direction of the difference
    # generate using Analysis.generateMplotStats()
    def plotComparisonStats(self, data, plot, plot_title, filename):

        filepath = self.outputPath + filename

        # first extract arrays to plot 90 and 95% confidence markers
        p95s = ([],[]) # ([xvalues][yvalues])
        p90s = ([],[])
        for i in range(len(data['p'])):
            if math.fabs(data['p'][i]) >= 0.95:
                p95s[0].append(data['x'][i])
                p95s[1].append(data['y'][i])
            elif math.fabs(data['p'][i]) >= 0.9:
                p90s[0].append(data['x'][i])
                p90s[1].append(data['y'][i])

        register_cmap(name='BlueRedAlpha', data=stats_colormap)

        # now do the plotting
        figure()

        # set axis limits - puts plot right way up
        ylim(-0.5, self.gridy-0.5)
        xlim(-0.5, self.gridx-0.5)

        # plot main data
        scatter(data['x'],data['y'],s=data['s'], c=data['p'])
        set_cmap('BlueRedAlpha')
        colorbar(shrink=0.8,aspect=10) # adds scale for colour map, shrunk slightly

        # plot 90 and 95% confidence markers
        scatter(p90s[0],p90s[1],s=20, c='orange')
        scatter(p95s[0],p95s[1],s=40, c='red')

        title(plot_title) # adds title
        ax = axes() # now hide the axis scales
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        axes().set_aspect('equal', 'datalim')
        savefig(filepath)
        return filename


    # #####
    # plot fixations from one or more participants
    def plotFixations(self, participants, filename, image=None):

        # alpha depends on number of participants
        if len(participants) > 1:
            alpha = 0.1
        else:
            alpha = 0.5

        xs = []
        ys = []
        durs = []
        ids = []
        i = 1
        figure()

        #if image is None:
        #    image = "/home/wel/andy/eye-tracking-analysis/4-news.png"

        if image is not None:
            try:
                im = imread(image)
                imshow(im, alpha=0.5, extent=[0,1280,0,1024])
            except IOError:
                print "no image"

        for p in participants:
            fixations = p.fixationList
            # alpha also depends on number of participants
            if len(fixations) > 100:
                alpha = 0.1

            for fix in fixations:
                xs.append(fix.x)
                ys.append(fix.y)
                durs.append(fix.duration)
                ids.append(i)
            scatter(xs,ys,s=durs,c=ids,alpha=alpha,label=p.number)
            i += 1
        xlim(0,1280)
        ylim(0,1024)
        ax = axes()
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.set_aspect('equal', 'datalim')
        # legend(scatterpoints=1, markerscale=0.5)
        savefig(filename)


    # #####
    # overlay plots of fixations from two datasets
    # dsA plotted in green, dsB in blue
    def plotFixationComparison(self, dsA, dsB, filename):
        xs = []
        ys = []
        durs = []
        #ids = []
        #i = 1
        figure()
        for p in dsA.participantList:
            fixations = p.fixationList
            for fix in fixations:
                xs.append(fix.x)
                ys.append(fix.y)
                durs.append(fix.duration)
        p1 = scatter(xs,ys,s=durs,c='g',alpha=0.1,label=dsA.label)
        xs = []
        ys = []
        durs = []
        for p in dsB.participantList:
            fixations = p.fixationList
            for fix in fixations:
                xs.append(fix.x)
                ys.append(fix.y)
                durs.append(fix.duration)
        p2 = scatter(xs,ys,s=durs,c='b',alpha=0.1,label=dsB.label)
        xlim(0,1280)
        ylim(0,1024)
        axes().set_aspect('equal', 'datalim')
        legend(scatterpoints=1, markerscale=0.5)
        savefig(self.outputPath + filename)


    # #####
    # generate a plot showing the gaze paths between boxes for a dataset
    def plotPaths(self, dataset, filename, image=None):
        gridx = self.gridx
        gridy = self.gridy
        numBoxes = gridx * gridy

        # collect data into matrix
        paths = dataset.participantList[0].generatePathData(gridx, gridy)
        mat = matrix(paths)
        for p in dataset.participantList[1:]:
            mat += matrix(p.generatePathData(gridx, gridy))

        # find max (between boxes) to scale with
        maxval = 0
        for i in range(numBoxes):
            for j in range(numBoxes):
                if i != j:
                    if mat[i,j] > maxval:
                        maxval = mat[i,j]
        print "Max = " + str(maxval)

        # plot
        figure()

        #if image is None:
        #    image = "/home/wel/andy/eye-tracking-analysis/4-news.png"

        if image is not None:
            try:
                im = imread(image)
                imshow(im, alpha=0.5, extent=[-0.5,self.gridx-.5,-0.5,self.gridy-.5])
            except IOError:
                print "no image"

        ylim(-0.5, self.gridy-.5)
        xlim(-0.5, self.gridx-.5)
        same = [[],[],[]]
        # plot an arrow for each path
        ax = plt.axes()
        ec = 0.01
        for i in range(numBoxes):
            for j in range(numBoxes):
                xa = i%gridx
                ya = i/gridx
                xb = j%gridx
                yb = j/gridx
                val = mat[i,j]/maxval
                if xa == xb and ya == yb:
                    same[0].append(xa)
                    same[1].append(ya)
                    same[2].append(val*150)
                elif val > 0.1:
                    ec = 0.01 + ec
                    rgbTuple = self.floatRgb(ec,0,1)
                    ax.arrow(xa, ya, xb-xa, yb-ya, head_width=0.5*val, alpha=(val), width=0.2*val, ec=rgbTuple,color=rgbTuple, length_includes_head=True)

        # plot within box paths
        scatter(same[0],same[1],s=same[2],alpha=0.4)

        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        # ax.set_aspect('equal', 'datalim')
        savefig(filename)

    # #####
    # Spot the artwork functions
    #
    #
    # #####
    def floatRgb(self,mag, cmin, cmax):
        """
        Return a tuple of floats between 0 and 1 for the red, green and
        blue amplitudes.
        """

        try:
            # normalize to [0,1]
            x = float(mag-cmin)/float(cmax-cmin)
        except:
            # cmax = cmin
            x = 0.5
        blue = min((max((4*(0.75-x), 0.)), 1.))
        red  = min((max((4*(x-0.25), 0.)), 1.))
        green= min((max((4*math.fabs(x-0.5)-1., 0.)), 1.))
        return (red, green, blue)

    def plotParticipantPaths(self,dataset,participantNum,filename,image=None):

        gridx = self.gridx
        gridy = self.gridy
        numBoxes = gridx * gridy


        # collect data into matrix
        paths = dataset.getParticipant(participantNum).generatePathData(gridx,gridy)
        #paths = dataset.participantList[0].generatePathData(gridx, gridy)
        mat = matrix(paths)
        #print mat
        # find max (between boxes) to scale with
        maxval = 0
        for i in range(numBoxes):
            for j in range(numBoxes):
                if i != j:
                    if mat[i,j] > maxval:
                        maxval = mat[i,j]
        print "Max = " + str(maxval)

        # plot
        figure()

        #if image is None:
        #    image = "/home/wel/andy/eye-tracking-analysis/4-news.png"

        if image is not None:
            try:
                im = imread(image)
                imshow(im, alpha=0.5, extent=[-0.5,self.gridx-.5,-0.5,self.gridy-.5])
            except IOError:
                print "no image"

        ylim(-0.5, self.gridy-.5)
        xlim(-0.5, self.gridx-.5)
        same = [[],[],[]]
        # plot an arrow for each path
        ax = plt.axes()
        ec = 0.01
        for i in range(numBoxes):
            for j in range(numBoxes):
                xa = i%gridx
                ya = i/gridx
                xb = j%gridx
                yb = j/gridx
                val = mat[i,j]/maxval
                if xa == xb and ya == yb:
                    same[0].append(xa)
                    same[1].append(ya)
                    same[2].append(val*150)
                elif val > 0.1:
                    rgbTuple = self.floatRgb(ec,0,1)
                    ec = 0.04 + ec
                    #print rgbTuple
                    ax.arrow(xa, ya, xb-xa, yb-ya, head_width=0.5*val, alpha=(val), width=0.2*val, color=rgbTuple, ec=rgbTuple ,
                             length_includes_head=True)


        # plot within box paths
        scatter(same[0],same[1],s=same[2],alpha=0.4)

        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        # ax.set_aspect('equal', 'datalim')
        savefig(filename)

    def plotArbitraryAOI(self,filename,image=None):

        fig=figure()
        ax = plt.axes()
        if image is not None:
            try:
                im = imread(image)
                imshow(im, alpha=0.5, extent=[-0.5,self.gridx-.5,-0.5,self.gridy-.5])
            except IOError:
                print "no image"


        el = Ellipse(40,500,150,43.0)
        ax.plot(el)

        savefig(filename)
