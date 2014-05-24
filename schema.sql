/*drop table recordings;
drop table datasets;*/
CREATE TABLE datasets (id INTEGER PRIMARY KEY, uid CHAR(36), filename TEXT, label TEXT, comment TEXT);
CREATE TABLE recordings (id INTEGER PRIMARY KEY, filename TEXT, participant CHAR(10), uid CHAR(36), notes TEXT, new_format BOOLEAN);
CREATE TABLE slice_contents(slice INTEGER REFERENCES slices, slice_index INTEGER, dataset INTEGER REFERENCES datasets);
CREATE TABLE slices (id INTEGER PRIMARY KEY, label TEXT, uid CHAR(36));
CREATE TABLE users (username CHAR(50) PRIMARY KEY, uid CHAR(36), password CHAR(30), email TEXT);
CREATE TABLE videos (dataset INTEGER PRIMARY KEY, filename TEXT, offset INTEGER);
