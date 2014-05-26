from flask import Flask, session, render_template, request, flash, redirect, url_for, g, jsonify, Markup
from werkzeug import secure_filename
import os
import analysis, plotting
import dataset as ds
import uuid
import sqlite3
import fnmatch

# import init values (paths)
from ini import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['VISUALISER_FOLDER'] = VISUALISER_FOLDER
app.config['VISUALISER_ROOT'] = VISUALISER_ROOT
app.config['DATABASE'] = DATABASE
# set the secret key.  keep this really secret:
app.secret_key = '+\xdc4\xdfr\x90\rV\x8c\xf5\x04\xd1\x93%\xd23e\xd1o\xf0\x93\x8a\xf7\x12'

# #####
# db functions
def connect_db():
    return sqlite3.connect(DATABASE)

from contextlib import closing

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('C:\\Users\\panos\\PycharmProjects\\eyeTracking\\eyeTracking\\schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

def query_db(query, args=(), one=False):

    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv
  

# #####
# get login details for user
def check_user(username):

    row = query_db('select * from users where username=?', [username], one=True)
    if row is None:
        return None, None
    uPass = row['password']
    uId = row['uid']
    return uPass, uId
    

# #####
# test if filename is in allowed list
def allowed_file(filename, extensions=ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in extensions

# #####
# returns an path to the directory where this users data are stored
def getUserDir():
    return os.path.join(app.config['UPLOAD_FOLDER'], str(session['uid']), '')

# #####
# returns an path to the directory where this users images are stored
def getUserImgDir():
    return os.path.join(app.config['IMAGE_FOLDER'], str(session['uid']), '')

# #####
# returns an path to the directory where this users visualitions are stored
def getUserVisDir():
    return os.path.join(app.config['VISUALISER_ROOT'], app.config['VISUALISER_FOLDER'], str(session['uid']), '')
    
# #####
# returns an analysis object and the requested dataset
def getDataset(id, an=None):
    row = query_db('select filename from datasets where id=?', [id], one=True)
    filenameA = row['filename']
    if not an:
        an = analysis.Analysis()
        an.outputPath = getUserImgDir()
    dsA = an.loadDataSet(filenameA)
    # reload parameters from dataset into analysis object
    an.params = dsA.parameters
    return an, dsA

# #####
# returns a string giving full path to background image for the requested dataset
# expected to be in uploads dir with label-bgim.png filename.
# may change to allow any file name and store name in db
def getBackgroundImage(ds):
    # get label
    label = ds.label
    filename = label + "-bgim.png"
    fullpath = os.path.join(getUserDir(), filename)
    return fullpath

# #####
# get the url and offset for video visualisation of this dataset
# returns None, None if nothing recorded
def getVideoData(id):
    row = query_db('select * from videos where dataset=?', [id], one=True)
    if row is None:
        return None, None
    return row['filename'], row['offset']


# #####
# gets a filename for the requested dataset
def getFilename(dsid):
    row = query_db('select filename from datasets where id=?', [dsid], one=True)
    filenameA = row['filename']
    return filenameA


# #####
# get a list of the recordings available for current user
# returns list of tuples (filename, participant id, comment, recording id)
def getRecordings():
    rows = query_db('select * from recordings where uid=? order by id ASC', [str(session['uid'])])
    recordings = [(r['filename'], r['participant'], r['notes'], r['id'], r['new_format']) for r in rows]
    return recordings


# #####
# get details of the recording with given filename 
# returns tuple (filename, participant id, comment, recording id)
def getRecordingDetailsByFilename(fname):
    r = query_db('select * from recordings where filename like ? and uid=?', [fname, str(session['uid'])], True)
    if r is not None:
        recording = (r['filename'], r['participant'], r['notes'], r['id'])
        return recording
    else:
        return None
    

# #####
# get details of the recording with given id 
# returns tuple (filename, participant id, comment, recording id)
def getRecordingDetailsById(id):
    r = query_db('select * from recordings where id=? and uid=?', [id, str(session['uid'])], True)
    if r is not None:
        recording = (r['filename'], r['participant'], r['notes'], r['id'])
        return recording
    else:
        return None
    

# #####
# remove a recording from the database, and remove the file
def removeRecording(id):
    # remove file
    row = query_db('select filename from recordings where id=?', [id], one=True)
    filename = os.path.join(getUserDir(), str(row['filename']))
    try:
        os.remove(filename)
    except:
        pass
    # remove from db
    g.db.execute('delete from recordings where id=?', [id])
    


# #####
# get (id, label) for all sets in given slice group
def getSetsInSlice(slice_id):
    cur = g.db.execute('select datasets.id, datasets.label from slice_contents left outer join datasets on datasets.id=slice_contents.dataset where slice=?', [slice_id])
    rows = cur.fetchall()
    dsets = [(r[0], r[1]) for r in rows] 
    return dsets

# #####
# get a string describing the plot type given plot number
def getStringForPlot(plot):
    if plot == 0:
        title = "Fixation count"
    elif plot == 1:
        title = "Total fixation duration"
    elif plot == 2:
        title = "Mean fixation duration"
    elif plot == 3:
        title = "Fixation frequency"
    elif plot == 4:
        title = "Time to first fixation"
    elif plot == 5:
        title = "Gaze paths"
    else:
        title = "Unknown"
    return title


# #####
# returns an array where index gives description for that plot number
def getPlotTranslator():
    trans = []
    for i in range(5):
        trans.append(getStringForPlot(i))
    return trans
        

# #####
# get a list of the datasets available for current user
def getDataSets():
    rows = query_db('select * from datasets where uid=?', [str(session['uid'])])
    dsets = [(r['label'], r['id'], r['filename'], r['comment']) for r in rows] 
    return dsets

# #####
# get details of the datasets with given id
# returns tuple
def getDataSetDetails(dsid):
    r = query_db('select * from datasets where id=?', [dsid], True)
    dset = (r['label'], r['id'], r['filename'], r['comment']) 
    return dset

# #####
# gets datasets grouped:
# individuals on their own, 
# slices grouped together
def getDataSetsGrouped():
    query = 'select datasets.label, datasets.id, datasets.filename, slices.id, slices.label, datasets.comment from datasets left outer join slice_contents on slice_contents.dataset=datasets.id left outer join slices on slices.id=slice_contents.slice where datasets.uid=? order by slices.id ASC, slice_contents.slice_index ASC'
    cur = g.db.execute(query,[str(session['uid'])])
    rows = cur.fetchall()

    # 0 -> ds label
    # 1 -> ds id
    # 2 -> ds filename
    # 3 -> slice id
    # 4 -> slice label
    # 5 -> ds comment

    dsgroups = []
    currentSliceId = "-1"
    currentSlice = ['', [], [], []] # slice label; ids; filenames; comments
    for r in rows:        
        if r[3] is None:
            # only one
            dsgroups.append((r[0], [r[1]], [r[2]], [r[5]]))
        elif str(r[3]) == str(currentSliceId):
            # add to group
            currentSlice[0] = r[4]
            currentSlice[1].append(r[1])
            currentSlice[2].append(r[0])
            currentSlice[3].append(r[5])
        else:
            # new group
            # save old one if it has any contents
            if len(currentSlice[1]) > 0:
                dsgroups.append((currentSlice[0], currentSlice[1], currentSlice[2], currentSlice[3], currentSliceId))
            currentSlice = [r[4], [str(r[1])], [str(r[0])], [r[5]] ]
            currentSliceId = str(r[3])
    # save final group if it has any contents
    if len(currentSlice[1]) > 0:
        dsgroups.append((currentSlice[0], currentSlice[1], currentSlice[2], currentSlice[3], currentSliceId))

    return dsgroups

# #####
# remove a dataset from the database, and remove the dataset and plot files
def removeDataset(id):
    # remove file
    row = query_db('select filename,label from datasets where id=?', [id], one=True)
    filename = os.path.join(getUserImgDir(), str(row['filename']))
    
    try:
        os.remove(filename)
    except:
        pass

    # remove plots...
    label = row['label']
    for file in os.listdir(getUserImgDir()):
        if fnmatch.fnmatch(file, label+"*png"):
            print "removing " + str(file)
            try:
                filename = os.path.join(getUserImgDir(), file)
                os.remove(filename)
            except:
                pass

    # remove from db
    g.db.execute('delete from datasets where id=?', [id])
    g.db.execute('delete from videos where dataset=?', [id])
    g.db.commit()


# #####
# get a tuple of data, including URL for image to given plot, creating it if it doesn't exist
def getPlot(ds, plot, an=None):
    if not an:
        an = analysis.Analysis()
        an.outputPath = getUserImgDir()
    plotFileName = ds.label + "_plot_" + str(plot) + ".png"
    plotOutputPath = os.path.join(getUserImgDir(), plotFileName)
    fileURL = str(session['uid']) + "/" + plotFileName
    plotUrl = url_for('static', filename=fileURL)

    title = getStringForPlot(plot)
        
    if True:#not os.path.isfile(plotOutputPath):
        if plot == 5:
            an.getPlotter().plotPaths(ds, plotOutputPath, getBackgroundImage(ds))
        else:
            # print "Creating plot " + str(plot) + " for " + ds.label
            an.getPlotter().plotDataSet(ds, plot, None, ds.label + ": " + title, plotOutputPath, getBackgroundImage(ds))

 
    return {'title': title, 'url': plotUrl, 'plot': plot}
        
# #####
# gets a participant number from a recording file
def getParticpantFromRecordingFile(filename, newstyle=False):
    participantId = "P?"
    col = None
    for dataline in open(filename):
        tokens = dataline.split("\t")
        if newstyle:
            if col is None:
                col = tokens.index("ParticipantName")
            else:
                participantId = tokens[col].strip()
                break
        else:       
            try:
                if tokens[0] == "Participant:":
                    participantId = tokens[1].strip()
                    break
            except:
                pass
    return participantId
    
# #####
# save a dataset and add to the database
def storeDataset(ds):
    dsFileLocation = os.path.join(getUserImgDir(), ds.label + ".xml")
    ds.saveToFile(dsFileLocation)
    cur = g.db.execute('insert into datasets (uid, filename, label) values(?,?,?)', [str(session['uid']), str(dsFileLocation), ds.label])
    lid = cur.lastrowid
    g.db.commit()
    return lid

# #####
# record a video in the database
# and save to appropriate location
def storeVideo(dsid, vidFile, offset):
    fname = secure_filename(vidFile.filename)
    vidFile.save(os.path.join(getUserVisDir(), fname))
    cur = g.db.execute('insert into videos (dataset, filename, offset) values(?,?,?)', [str(dsid), fname, str(offset)])
    g.db.commit()


# ##################################################################################
# Routing functions
# ##################################################################################

# #####
# filter to format numbers
# numbers over 100 rounded to integers,
# numbers less shown to 3 significant figures
@app.template_filter('sigfigs')
def sig_digits(x, n=3):
    if str(x) == 'nan':
        return '-'
    
    if x >= 100:
        return int(round(x))
    
    # Use %e format to get the n most significant digits, as a string.
    format = "%." + str(n-1) + "e"
    r = format % x
    answer = float(r)
    # if it's an integer, return it as an integer
    if int(answer) == answer:
        return int(answer)

    # it would also be nice to do something with exponential notation...
    return answer

# #####
# filter to format numbers to have same number of characters after decimal point
# padded with html spaces
@app.template_filter('decplaces')
def decimal_places(x, n=5):
    if str(x) == 'nan':
        return '-'
    
    if str(x) == '-':
        return '-'
    
    if "e" in str(x) or str(x) == "0":
        return x

    if "." not in str(x):
        return Markup(str(x) + "&nbsp;"*(n+1))

    pos = str(x).find(".")
    length = len(str(x))
    dps = length - pos - 1
    # print str(x) + ": p=" + str(pos) + "; l=" + str(length) + "; d=" + str(dps)
    if dps < n:
        x = str(x) + "&nbsp;"*(n-dps)
    return Markup(x)
    

# #####
# filter to format numbers
# numbers over 100 rounded to integers,
# numbers less shown to 3 significant figures
@app.template_filter('show_p')
def highlightP(p):
    if str(p) == 'nan' or str(p) == "-":
        return p
    
    if p <= 0.05:
        return Markup("<span class=p95>" + str(p) + "</span>")
    
    if p <= 0.1:
        return Markup("<span class=p90>" + str(p) + "</span>")
    
    return Markup("<span class=minor>" + str(p) + "</span>")

# register 
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        upass, uId = check_user(request.form['username'])
        if upass is not None:
            error = 'Username already in use'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            uId = uuid.uuid4()
            session['uid'] = uId
            g.db.execute('insert into users (username, password, uid) values(?,?,?)', [request.form['username'], request.form['password'], str(uId)])
            g.db.commit()
            session.permanent = True
            userdir = getUserDir()
            userImgDir = getUserImgDir()
            visDir = getUserVisDir()
            # make a folder for this user..
            if not os.path.exists(userdir):
                os.makedirs(userdir)
            # make a folder for this user..
            if not os.path.exists(userImgDir):
                os.makedirs(userImgDir)
            # make a folder for visualisations for this user..
            if not os.path.exists(visDir):
                os.makedirs(visDir)
            return redirect(url_for('upload_file'))
    return render_template('login.html', error=error)

# login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        upass, uId = check_user(request.form['username'])
        if upass is None:
            error = 'Invalid username'
        elif request.form['password'] != upass:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            session['uid'] = uId
            session.permanent = True
            userdir = getUserDir()
            userImgDir = getUserImgDir()
            return redirect(url_for('upload_file'))
    return render_template('login.html', error=error)

# log out 
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('uid', None)
    flash('You were logged out')
    return render_template('login.html')
    # return redirect(url_for('show_entries'))

@app.route("/")
def home():
    if not 'logged_in' in session:
        return redirect(url_for('login'))

    return redirect(url_for('upload_file'))

@app.route("/about/")
def about():
    return render_template('about.html')

# #####
# Allow users to upload recordings, 
# and process them
@app.route("/upload/", methods=['GET', 'POST'])
def upload_file():
    if not 'logged_in' in session:
        error = "Please log in before uploading"
        return render_template('login.html', error=error) 

    if request.method == 'POST':
        newstyle = 'newformat' in request.form
            # print "uploading new format tsv file"
        files = request.files.getlist('file')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print filename
                file.save(os.path.join(getUserDir(), filename))
                pid = getParticpantFromRecordingFile(os.path.join(getUserDir(), filename), newstyle)
                print pid
                g.db.execute('insert into recordings (uid, filename, participant, new_format) values(?,?,?,?)', [str(session['uid']), str(filename), pid, newstyle])
            else:
                flash("error uploading " + file.filename + ": only tsv files accepted")
                return redirect(url_for('upload_file'))
        g.db.commit()

        return redirect(url_for('recordings'))
    else:
        return render_template('start.html')


# #####
# show a list of recordings, allowing users to comment and delete, or upload more
@app.route('/recordings/')
def recordings():
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 

    recordings = getRecordings()
    return render_template('recordings.html', recs=recordings)


# #####
# make changes to the list of recordings:
# process comments and deletions
@app.route('/_mod_recordings/', methods=['POST'])
def modify_recordings():
    recordings = getRecordings()
    # save comments to db
    deletes = request.form.getlist('delete')
    for rem in deletes:
        removeRecording(rem)
    for r in recordings:
        comment = request.form['note' + str(r[3])]
        if comment != str(r[2]):
            g.db.execute('update recordings set notes=? where id=?', [comment, r[3]])
    g.db.commit()
    return redirect(url_for('recordings'))


# #####
# view the fixation plot for a segment of a recording
@app.route('/dataset/<int:id>/fixations/<int:rec>/')
def view_recording(id, rec):
    an, ds = getDataset(id)
    participants = ds.participantList
    p = participants[rec]
    filename = ds.label + "_" + str(p.number).strip() + "fixplot.png"
    plotOutputPath = os.path.join(getUserImgDir(), filename)
    an.getPlotter().plotFixations([p], plotOutputPath, getBackgroundImage(ds))
    fileurl = str(session['uid']) + "/" + filename
    ploturl = url_for('static', filename=fileurl)
    title = 'Fixation plot for ' + p.number + " between " + str(p.startTime) + " and " + str(p.endTime) + "ms"
    pageTitle = "Fixation plot for " + p.number + ", " + ds.label
    plots =  [(ploturl, title)]
    return render_template('recording.html', title=pageTitle, plots=plots)

    
# #####
# view the fixation plot for a segment of a recording
@app.route('/dataset/<int:id>/fixations/all/')
@app.route('/dataset/<int:id>/fixations/')
def view_recordings(id):
    an, ds = getDataset(id)
    participants = ds.participantList
    filename = ds.label + "_all_fixplot.png"
    plotOutputPath = os.path.join(getUserImgDir(), filename)
    an.getPlotter().plotFixations(participants, plotOutputPath, getBackgroundImage(ds))
    ploturl = url_for('static', filename=str(session['uid']) + "/" + filename)
    title = 'Fixation plot for all participants'
    plots = [(ploturl, title)]
    pageTitle = title + ', ' + ds.label
    for p in participants:
        filename = ds.label + "_" +  str(p.number).strip() + "fixplot.png"
        plotOutputPath = os.path.join(getUserImgDir(), filename)
        an.getPlotter().plotFixations([p], plotOutputPath, getBackgroundImage(ds))
        ploturl = url_for('static', filename=str(session['uid']) + "/" + filename)
        title = p.number + ", " + str(p.startTime) + " to " + str(p.endTime) + "ms"
        plots.append((ploturl, title))
         
    return render_template('recording.html', title=pageTitle, plots=plots)


# #####
# view the fixations played over the video
@app.route('/dataset/<int:id>/visualiser/')
def visualise_video(id):
    an, ds = getDataset(id)
    vid_file, vid_offset = getVideoData(id)
    if vid_file is None:
        flash("There is no video associated with this dataset")
        return redirect(url_for('viewDataset', id=id))

    print "Creating visualisation " + str(vid_file) +", " + str(vid_offset)
    relativePath = os.path.join(app.config['VISUALISER_FOLDER'], str(session['uid']), '')
    ds.createVisualiserFiles(app.config['VISUALISER_ROOT'], relativePath, vid_file=vid_file, vid_offset=vid_offset)
    visualiser_path = '/index.html?manifest=' + relativePath + ds.label + "-manifest.json"
    # return redirect(url_for('static', filename='subseyevis/iframe.html'))
    return render_template('visualiser.html', visurl=VISUALISER_URL+visualiser_path, label=ds.label)

    
# #####
# show a list of datasets, and allow users to upload more
@app.route('/dataset/')
@app.route('/datasets/')
@app.route('/dataset/all/')
def all_datasets():
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 

    return render_template('datasets.html', sets=getDataSetsGrouped(), userdir=os.path.join( str(session['uid']), ''))#, allsets=getDataSets())

    
# #####
# process a new dataset
# or show list of those available    
@app.route('/dataset/new/', methods=['GET', 'POST'])
def createDataset():
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 

    if request.method == 'POST':
        # create new dataset(s)

        # normal or time-sliced?
        time_slice = False
        time_split = False
        if  'timeDs' in request.form:
            sliceLength = int(request.form['slicetime'])
            time_slice = True            
        elif  'offsetDs' in request.form:
            offsets = request.form['sliceoffsets']
            time_split = True 
            

        # times or stimulus?
        stimulus = False
        if 'stimulus' in request.form:
            stimId = request.form['stimulus']
            if stimId != "":
                stimulus = True            

        # get analysis parameters
        error = int(request.form['Errorradius'])
        group = int(request.form['Groupingradius'])
        filter_r = int(request.form['Lengthfilter'])
        gridx = int(request.form['Gridwidth'])
        gridy = int(request.form['Gridheight'])
        params = {
            'errorRadius': error, 
            'gridWidth': gridx,   
            'gridHeight': gridy,
            'groupingRadius': group,
            'fixationLengthFilter': filter_r
            }

        # work out which recordings are included
        recs = getRecordings()
        includes = request.form.getlist('include')
        label = str(request.form['label'])
        filelist = []
        targetTimes = []
        for check in includes:
            index = int(check)-1
            # are they old or new format?  Assume all the same...
            newFormat = recs[index][4]
            print "format = " + str(newFormat)
            if newFormat:
                print "creating dataset from new-format recordings"

            filelist.append(str(recs[index][0]))
            try:
                start = int(request.form['start' + check])
            except:
                start = None
            try:
                end = int(request.form['end' + check])
            except:
                end = None
            targetTimes.append([start, end])

        # background image
        file = request.files['image_file']
        if file and allowed_file(file.filename, ['png']):
            filename = secure_filename(file.filename)
            print "Saving bg img file: " + filename
            file.save(os.path.join(getUserDir(), label + "-bgim.png"))

        # video
        vfile = request.files['video_file']
        if vfile and not allowed_file(vfile.filename, ['webm']):
            vfile = None
        voffset = request.form['videoOffset']
 
        #  now build dataset(s)
        an = analysis.Analysis(params)
        an.outputPath = getUserDir()
        if time_slice or time_split:
            if time_slice:
                datasets = an.generateTimeSlicedDataSets(label, filelist, targetTimes, sliceLength, getUserDir())
            else:
                offsetArray = [int(x.strip()) for x in offsets.split(',')]
                datasets = an.generateTimeSplitDataSets(label, filelist, targetTimes, offsetArray, getUserDir())
            # also put in slices table
            cur = g.db.execute('insert into slices (label, uid) values(?,?)', [label, str(session['uid'])])
            slice_id = cur.lastrowid           
            # now save them
            counter = 1
            for set in datasets:
                lid = storeDataset(set)
                cur = g.db.execute('insert into slice_contents (slice, slice_index, dataset) values(?,?,?)', [slice_id, counter, lid])
                counter += 1
            g.db.commit()            

        elif stimulus:
            ds = an.buildDataSetForStimulus(label, filelist, stimId, inputFilePath=getUserDir(), newRecordingFormat=newFormat)
            an.analyseDataSet(ds)
            lid = storeDataset(ds)
            if vfile is not None:
                storeVideo(lid, vfile, voffset)

        else:
            ds = an.buildDataSet(label, filelist, targetTimes, inputFilePath=getUserDir(), newRecordingFormat=newFormat)
            an.analyseDataSet(ds)
            lid = storeDataset(ds)
            if vfile is not None:
                print str(vfile)
                storeVideo(lid, vfile, voffset)

        # now display it/them
        if len(filelist) > 1:
            return redirect(url_for('all_datasets'))
        else:
            return redirect(url_for('viewDataset', id=lid))
    else:
        # getDataSetsGrouped()
        # just display what we have
        return render_template('createDataset.html', recs=getRecordings())

# #####
# show the results of analysis on a dataset
@app.route('/dataset/<id>/', methods=['GET', 'POST'])
def viewDataset(id):
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 

    details = getDataSetDetails(id)
    comment = details[3]

    an = analysis.Analysis()
    an.outputPath = getUserDir()
    an, ds = getDataset(id)
    # if not dataset analysed...:
    # an.getPlotter().generatePathPlotData(ds, "test.png")

    # now get plots
    plots = []

    # is there a video visualisatoin
    vid_f, offset = getVideoData(id)
    has_video = vid_f is not None

    for i in range(6):
        plots.append(getPlot(ds, i, an))

    p_details = []
    participants = ds.participantList
    for p in participants:
        recording = getRecordingDetailsByFilename(p.fileName)
        p_comment = None
        if recording is not None:
            p_comment = recording[2]
        this_p = (p.fileName, p.startTime, p.endTime, len(p.fixationList), p.number, p_comment)
        p_details.append(this_p)

    return render_template('set.html', dsid=id, label=ds.label, participants=p_details, plots=plots, comment=comment, sets=getDataSets(), params=ds.parameters, stimulus=ds.targetStimulus, video=has_video)


# #####
# Allow users to upload datasets, 
# and view them
@app.route("/upload/dataset/", methods=['GET', 'POST'])
def upload_dataset():
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 

    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                fileFullPath = os.path.join(getUserDir(), filename)
                file.save(fileFullPath)
                an = analysis.Analysis()
                ds = an.loadDataSet(fileFullPath)
                cur = g.db.execute('insert into datasets (uid, filename, label) values(?,?,?)', [str(session['uid']), str(fileFullPath), ds.label])
                dataset_id = cur.lastrowid
            else:
                flash("error uploading " + file.filename + ": only data files accepted")
                return redirect(url_for('upload_file'))
        g.db.commit()
        if len(files) > 1:
            return redirect(url_for('viewDataset'))
        return redirect(url_for('viewDataset', id=dataset_id))
    else:
        return render_template('start.html')
  
# #####
# make changes to the list of datasets:
# process comments and deletions
@app.route('/_mod_datasets/', methods=['POST'])
def modify_datasets():
    sets = getDataSets()
    print "Modifying datasets"
    deletes = request.form.getlist('delete')
    for rem in deletes:
        print "Remove dataset " + str(rem)
        removeDataset(rem)
    for s in sets:
        comment = request.form['note' + str(s[1])]
        if comment != str(s[3]):
            print "Save comment for " + str(s[1])
            g.db.execute('update datasets set comment=? where id=?', [comment, s[1]])
        
    g.db.commit()        
    return redirect(url_for('all_datasets'))
    

# #####
# display all plots in a time-slice series
@app.route('/slice/<id>/')
@app.route('/slice/<id>/<plot>/')
def allSlices(id, plot='3'):
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 

    # get id, label for all datasets in slice
    sets = getSetsInSlice(id)

    an = analysis.Analysis()
    an.outputPath = getUserImgDir()
    plots = []
    # get plot for each dataset
    for s in sets:
        an, ds = getDataset(s[0], an)
        plot_details = getPlot(ds, int(plot), an)
        plot_details['title'] = s[1]
        plots.append(plot_details)

    # we want to print links to show other plots - need a translator
    trans =  getPlotTranslator()

    # get label for slice
    label_q = query_db('select label from slices where id=?', [id], True)
    slice_label = label_q['label']

    return render_template('sliceSet.html', label=slice_label, sets=sets, plot_type="Fixation frequency", plots=plots, setid=id, translator=trans)


# #####
# show the results of comparison of two datasets
@app.route('/_compare', methods=['POST'])
def compare():
    # first parse value
    try:
        selected = request.form['compare']
    except:
        return redirect(url_for('viewDataset'))

    # print selected
    sets = getDataSets()
    setA = None
    setB = None
    for setOne in sets:
        for setTwo in sets:
            if selected == str(setOne[1]) + "_vs_" + str(setTwo[1]):
                return redirect(url_for('compareSets', ida=str(setOne[1]), idb=(setTwo[1])))
               # return "Compare " + str(setOne[1]) + " vs " + str(setTwo[1])
                setA = setOne
                setB = setTwo
                break

    return redirect(url_for('viewDataset'))

# #####
# show the results of comparison of two datasets
@app.route('/dataset/compare/<ida>/<idb>/', methods=['GET'])
def compareSets(ida, idb):
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 
 
    an = analysis.Analysis()
    an.outputPath = getUserImgDir()

    an, dsA = getDataset(ida, an)
    an, dsB = getDataset(idb, an)

    # fixation plot
    filename = dsA.label + "_vs_" + dsB.label + "-fixations.png"
    an.getPlotter().plotFixationComparison(dsA, dsB, filename)

    # get plot
    imageURL = url_for('static', filename=str(session['uid']) + "/" + filename)
    diagram = {'title': "Fixation plot for " + dsA.label + " and "+ dsB.label, 'url':imageURL, 'plot': 6 }

    # get details for table
    statsArray = None #an.getCompArray(dsA, dsB, plot)

    # render
    return render_template('compare.html', plot=diagram, labelA=dsA.label, labelB=dsB.label, id=[ida,idb], translator=getPlotTranslator())
            

@app.route('/dataset/compare/<ida>/<idb>/<int:plot>/', methods=['GET'])
def compareSetDetails(ida, idb, plot=3):
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 

  
    an = analysis.Analysis()
    an.outputPath = getUserImgDir()

    an, dsA = getDataset(ida, an)
    an, dsB = getDataset(idb, an)

    # get plot
    diff, data = an.generateMplotStats(dsA, dsB, plot)
    filename = dsA.label + "_vs_" + dsB.label + "-" + str(plot) + ".png"
    compImg = an.getPlotter().plotComparisonStats(data, plot, getStringForPlot(plot), filename)
    imageURL = url_for('static', filename=str(session['uid']) + "/" + compImg)
    diagram = {'title': "Comparison of " + dsA.label + " and "+ dsB.label, 'url':imageURL, 'plot': plot }

    # get details for table
    statsArray = an.getCompArray(dsA, dsB, plot)

    # render
    return render_template('compare.html', labelA=dsA.label, labelB=dsB.label, plot=diagram, boxes=statsArray, gridx=dsA.parameters['gridWidth'], gridy=dsA.parameters['gridHeight'], id=[ida,idb])
            

# #####
# show the detailed (tabulated numbers) results for a datasets
@app.route('/dataset/<id>/details/<int:plot>/', methods=['GET'])
def showDetails(id, plot):
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 

    an, ds = getDataset(id)
    
    if plot == 5:
        tableData = None
    else:
        tableData = an.getBoxArray(ds, plot)
    plot = getPlot(ds, plot, an)
    return render_template('details.html', label=ds.label, boxes=tableData, gridx=ds.parameters['gridWidth'], gridy=ds.parameters['gridHeight'], plot=plot, dsid=id)


# #####
# show the details of one box: value for each participant
@app.route('/dataset/<id>/details/<int:plot>/box/<int:x>,<int:y>/', methods=['GET'])
def boxDetails(id, plot,x,y):
    if not 'logged_in' in session:
        error = "Please log in"
        return render_template('login.html', error=error) 

    an, ds = getDataset(id)
    try:
        tableData, stats = an.getBoxData(ds, plot, (x, y))
    except IndexError:
        flash("You cannot view the details for box (" + str(x+1) + ", " + str(y+1) + ").  The grid size is " + str(ds.parameters['gridWidth'])  + " by " + str(ds.parameters['gridHeight']))
        return redirect(url_for('showDetails', id=id, plot=plot))
    recordings = []
    for p in ds.participantList:
        recordings.append((p.fileName, p.number))

    # test that we have equal numbers of participants and their data
    if len(tableData) != len(recordings):
        return "error"

    # only return stats if n > 1
    if len(tableData) <= 1:
        stats = None

    coords = [x,y]

    return render_template('boxTable.html', recordings=recordings, dataA=tableData, statsA=stats, box=coords)

# #####
# show the results of comparison of two datasets
@app.route('/_box_details', methods=['GET'])
def getBoxDetails():
    x = request.args.get('x', 0, type=int)
    y = request.args.get('y', 0, type=int)
    plot = request.args.get('plot', 0, type=int)
    id = request.args.get('id', 0, type=int)
    out = boxDetails(id, plot,x,y)
    return jsonify(result=out)


# #####
# show the results of comparison of two datasets
@app.route('/_compare_box_details', methods=['GET'])
def getBoxComparisonDetails():
    x = request.args.get('x', 0, type=int)
    y = request.args.get('y', 0, type=int)
    plot = request.args.get('plot', 0, type=int)
    idA = request.args.get('ida', 0, type=int)
    idB = request.args.get('idb', 0, type=int)
    an, dsA = getDataset(idA)
    an, dsB = getDataset(idB)
    try:
        tableDataA, statsA = an.getBoxData(dsA, plot, (x, y))
        tableDataB, statsB = an.getBoxData(dsB, plot, (x, y))
    except IndexError:
        flash("You cannot view the details for box (" + str(x+1) + ", " + str(y+1) + ").  The grid size is " + str(ds.parameters['gridWidth'])  + " by " + str(ds.parameters['gridHeight']))
        return redirect(url_for('showDetails', id=id, plot=plot))
    recordings = []
    for p in dsA.participantList:
        recordings.append((p.fileName, p.number))

    # test that we have equal numbers of participants and their data
    if len(tableDataA) != len(recordings):
        return "error"

    # only return stats if n > 1
    if len(tableDataA) <= 1:
        stats = None

    coords = [x,y]
    out =  render_template('boxTable.html', recordings=recordings, dataA=tableDataA, dataB=tableDataB, statsA=statsA, statsB=statsB, box=coords)
    return jsonify(result=out)


# #####
# run the web app
if __name__ == "__main__":

    app.debug = True
    app.run('0.0.0.0', 8080)
