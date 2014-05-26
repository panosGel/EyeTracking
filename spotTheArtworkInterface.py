__author__ = 'panos'
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

#return an analysis object and a requested dataset from the raw fixation data
def getDataset(id,an=None):
