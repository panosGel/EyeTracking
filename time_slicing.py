# ####################################################
# time_slicing.py
#
# ###############
#
# some functions that take a dataset, and divide it into time slices
#
# smoothing is carried out within this module, rather than using 
# the dataset smoothing, as it is rougher but much faster
# 

import numpy as np


##
# get the total amount of time participant spends fixating each box
# within given time period t1-t2
#
# returns dictionary of boxid->time, including all boxes with some attention
#
def getBoxesForParticipant(t1, t2, p, grid, smooth_radius=20):
    # print "getting",p.number,t1, t2
    # go through each fixation and get duration within slice
    results = {}
    for fix in p.fixationList:
        start = fix.time
        end = fix.time+fix.duration
        duration = 0
        if start > t2 or end < t1:
            # no overlap
            pass
        elif start < t1:
            # starts before this window, may end during or after...
            if end > t2:
                duration = t2-t1
            else:
                duration = end - t1
        elif end > t2:
            # ends after this window, but started during
            duration = t2 - start
        else:
            # wholly in window
            duration = end - start

        # if some time overlap, record
        if duration > 0:
            # may need to smooth over other boxes if near edge(s)
            # set smooth_radius to 0 if no smoothing required
            splits = splitFixation(fix.x, fix.y, smooth_radius, grid)
            for box in splits:
                boxId = box[0]
                prop = box[1]
                if boxId in results.keys():
                    results[boxId] += duration*prop
                else:
                    results[boxId] = duration*prop
                 
    return results


##
# get the id of a box (linearises grid)
def getBoxId(x, y, (grid_i, grid_j, boxWidth, boxHeight)):
    xBoxId = int(x/boxWidth)
    yBoxId = int(y/boxHeight)
    id = xBoxId+int(yBoxId*grid_i)
    # print x,y,id
    return id


##
# get the coordinates of the centre of a box with given (linear) id
def getCenterCoords(boxId, (grid_i, grid_j, boxWidth, boxHeight)):
    # convert back to grid index
    i = boxId%grid_i
    j = boxId/grid_i
    # and then to coordinates
    x = (i+0.5) * boxWidth
    y = (j+0.5) * boxHeight
    return (x,y)


# get a list of boxes with proportion of attention allocated to each within this slice
# sorted by attention (biggest first)
# in format ((x,y), attn) for each box, where x,y are coordinates of box centre
#   and attn is proportion of attention (duration) of all participants received
#   by each box
def getBoxesForTime(slice_length, slice_no, p_data, grid, radius):

    # print 'slice',slice_no
    all_results = {} # key = boxid (linear), value = total attention

    # accumulate data for all participants
    for p in p_data:
        offset = p.startTime
        t1 = offset + slice_no*slice_length
        t2 = offset + (slice_no+1)*slice_length
        boxes = getBoxesForParticipant(t1, t2, p, grid, radius)
        for box in boxes.keys():
            if box in all_results.keys():
                all_results[box] += boxes[box]
            else:
                all_results[box] = boxes[box]

    # print len(all_results.keys()),'boxes attended in slice',slice_no

    # now fill unattended boxes
    for boxid in range(0,grid[0]**2):
        if boxid not in all_results.keys():
            all_results[boxid] = 0

    # convert dict to list, and sort
    results = all_results.items()
    results.sort(key=lambda box: box[1], reverse=True)

    # get total attention, so we can calculate proportion
    total = sum([box[1] for box in results])

    # create a list with ((x,y), prop) for each box, with (x,y) box centre coordinates
    if total == 0:
        # if no attention, can't scale...
        sorted_list = [(getCenterCoords(box[0], grid),0) for box in results]
    else:
        # sorted by prop
        sorted_list = [(getCenterCoords(box[0], grid),float(box[1])/total) for box in results]

    return sorted_list


# ##
# get the mean and stdev for this box over this slice across all participants
def getBoxDataForTime(slice_length, slice_no, p_data, boxid, grid):

    # print 'slice',slice_no
    results = []

    # accumulate data for all participants over one box
    # as a list of values per p, so we can calculate mean and sd
    count = 0
    for p in p_data:
        offset = p.startTime
        t1 = offset + slice_no*slice_length
        t2 = offset + (slice_no+1)*slice_length
        boxes = getBoxesForParticipant(t1, t2, p, grid)
        if boxid in boxes.keys():
            results.append(boxes[boxid])
            count += 1
        else:
            results.append(0)
       
    if count > 5: # arbitrary!
        if np.std(results) > 500:
            print results
        return (np.mean(results), np.std(results), count)
    if count > 1: # arbitrary!
        return (np.mean(results), 0, count)
    else:
        return (0, 0, 0)
                       

# ##
# return an array of boxids with proportion allocated to each from this position
#    returns list of (boxid, proportion) tuples
#    all proportions will add to 1
# radius gives a distance to smooth over, but will limit itself to 
# requires grid dimensions (grid width, grid height, box width, box height)
def splitFixation(x,y, radius, (width, height, boxWidth, boxHeight)):

    # can't have radius bigger than half boxes
    if radius > float(boxWidth)*0.4 or radius > float(boxHeight)*0.4:
        radius = 0.4 * min([boxWidth, boxHeight])

    xBoxId = int(x/boxWidth)
    yBoxId = int(y/boxHeight)
    boxid = xBoxId+int(yBoxId*width)
    box_left_boundary = xBoxId*boxWidth
    box_top_boundary = yBoxId*boxHeight
    delta_x = x - box_left_boundary
    delta_y = y - box_top_boundary

    # is fix close to L or R boundary?
    split_x = 0
    if delta_x < radius:
        split_x = -1
    elif delta_x > (boxWidth-radius):
        split_x = 1

    # is fix close to L or R boundary?
    split_y = 0
    if delta_y < radius:
        split_y = -1
    elif delta_y > (boxHeight-radius):
        split_y = 1
     
    # simple case - in middle of box - do not split
    if split_x == 0 and split_y == 0:
        return [(boxid, 1)]

    # near one or more edges - work out how to share
    # if edge box, might not be able to split - keep values as False
    # otherwise set to 
    #    ('other':id of other, 'split':proportion in this)
    xsplit = False
    ysplit = False

    # split along x dimension
    if split_x == -1:
        if xBoxId > 0:  # share with last
            xsplit = {'split': getShareRatio(delta_x, radius), 'other': boxid-1}
    elif split_x == 1:
        if xBoxId < width - 1:  # share with next
            xsplit = {'split': getShareRatio(boxWidth-delta_x, radius), 'other': boxid+1}

    # split along y dimension
    if split_y == -1:
        if yBoxId > 0:  # share with last
            ysplit = {'split': getShareRatio(delta_y, radius), 'other': boxid-width}
    elif split_y == 1:
        if yBoxId < height - 1:   # share with next
            ysplit = {'split': getShareRatio(boxHeight-delta_y, radius), 'other': boxid+width}

    # now if xsplit or ysplit are still False, we don't split on that axis
    if not xsplit and not ysplit: # near an edge - do not split
        return [(boxid, 1)]
    # otherwise, they contain (otherbox, prop), giving id of box to share with
    # and proportion held by original
    elif not xsplit: # split y only
        return [(boxid, ysplit['split']), (ysplit['other'],1-ysplit['split'])]
    elif not ysplit: # split x only
        return [(boxid, xsplit['split']), (xsplit['other'],1-xsplit['split'])]
    else: # split both
        main_share = (boxid, xsplit['split']*ysplit['split'])
        x_share = (xsplit['other'], (1-xsplit['split'])*ysplit['split'])
        y_share = (ysplit['other'], (1-ysplit['split'])*xsplit['split'])
        # remainder of proportion goes to corner
        corner = 1 - sum([others[1] for others in [main_share, x_share, y_share]])
        # need to calculate id of corner
        corner_share = (ysplit['other'] - (boxid - xsplit['other']), corner)
        return [ main_share, x_share, y_share, corner_share ]
    
# ##
# share across two boxes according to:
#   delta - distance from edge of main box
#   radius - smoothing radius  
# returns proportion due to main box  
def getShareRatio(delta, radius):
    return 1 - (0.5 * float(delta)/radius)


# ##############################################################################

# ##
# test the splitting function
def testSplitter():
    # 10*8
    # 129*129 pixel boxes
    grid = (10,8,129,129)
    radius = 25
    # centre
    spl = splitFixation(50, 50, radius, grid) # centre of 0
    print [s[0] for s in spl] == [0]
    # near bottom
    spl = splitFixation(50, 120, radius, grid) # 0 and 10
    print [s[0] for s in spl] == [0, 10]
    # near left
    spl = splitFixation(140, 50, radius, grid) # 1 and 0
    print [s[0] for s in spl] == [1, 0]
    # near right
    spl = splitFixation(120, 50, radius, grid) # 0 and 1
    print [s[0] for s in spl] == [0, 1]
    # near top
    spl = splitFixation(160, 140, radius, grid) # 11 and 1
    print [s[0] for s in spl] == [11, 1]
    # near top R (but corner)
    spl = splitFixation(1270, 10, radius, grid) # 9 only
    print [s[0] for s in spl] == [9]
    # near bottom R (but R edge)
    spl = splitFixation(1270, 120, radius, grid) # 9 and 19
    print [s[0] for s in spl] == [9, 19]
    # centre
    spl = splitFixation(170, 170, radius, grid) # centre of 11
    print [s[0] for s in spl] == [11]
    # near to L (but corner)
    spl = splitFixation(10, 10, radius, grid) # 0 only
    print [s[0] for s in spl] == [0]
    # near L, but edge
    spl = splitFixation(10, 50, radius, grid) # 0 only
    print [s[0] for s in spl] == [0]
    # centre
    spl = splitFixation(50, 1020, radius, grid) # 70 only
    print [s[0] for s in spl] == [70]
    # near top left of 11
    spl = splitFixation(140, 130, radius, grid) # 11,10,1 and 0
    print [s[0] for s in spl] == [11, 10, 1, 0]
    # near bottom left of 11
    spl = splitFixation(140, 250, radius, grid) # 11,10,21 and 20
    print [s[0] for s in spl] == [11, 10, 21, 20]
    # near bottom right of 11
    spl = splitFixation(250, 250, radius, grid) # 11,12,21 and 22
    print [s[0] for s in spl] == [11, 12, 21, 22]
    # near top right of 11
    spl = splitFixation(250, 140, radius, grid) # 11,12,1 and 2
    print [s[0] for s in spl] == [11, 12, 1, 2]

# testSplitter()


##
# collect data
# returns a list of mode data:
#    each item in list is [x, y, attention proportion, start time]
def collectData(dataset, (number_slices, slice_length), grid, radius):
    participants = dataset.participantList
    out = [] 
    for data_slice in range(0, number_slices):
        all_boxes = getBoxesForTime(slice_length, data_slice, participants, grid, radius)
        # most attended is first in list
        (x_mode,y_mode), count = all_boxes[0] #, (mean,sd) = all_boxes[0]
        out.append([x_mode,y_mode,count,data_slice*slice_length])
    return out 

