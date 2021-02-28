#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import datetime as dt
import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Establishing a connection
engine = create_engine("sqlite:///./resources/hawaii.sqlite")

# To reflect classes
Base = automap_base()

Base.prepare(engine, reflect = True)

# Test out reflection
# Base.classes.keys()

# Alias for measurement and station classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create new session of engine
session = Session(engine)

# Flask
app = Flask(__name__)

# Route for home page displays available routes.
@app.route("/")
def home():
    return (
        f"Hello! Thanks for checking out the Hawaiian Climate API.<br>"
        f"Here are the available routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

# Precipitation route converts previous year's precipitation to a dictionary using date as the key and prcp as the value.
# Returns the JSON representation of the dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Data for previous year
    previous_year = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    
    # Query to get precipitation and date of measurement
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).all()
    
    # Save the query results as a dictionary and return it as JSON
    prcp_dict = {date: prcp for date, prcp in precipitation}
    
    return jsonify(prcp_dict)

# Stations route returns a JSON list of stations from which measurements were taken
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    
    stations = list(np.ravel(results))
    
    return jsonify(stations)

# TOBS route returns temperature observations for the most active stations for the last year of data
# Returns a JSON  list of temperatures
@app.route("/api/v1.0/tobs")
def temp_monthly():
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previous_year).all()
    
    temps = list(np.ravel(results))
    
    return jsonify(temps)

# These routes return temperature observation data for users if they enter start, or start & end, dates
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start = None, end = None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        temps = list(np.ravel(results))
        
        return jsonify(temps)
  
    results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        
    temps = list(np.ravel(results))
        
    return jsonify(temps)

if __name__ == "__main__":
    app.run()

