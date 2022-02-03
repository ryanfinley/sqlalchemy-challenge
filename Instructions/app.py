from turtle import st
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify, render_template

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    print("Server accessed the Home route")
    return("This is the Home page<br/>"
        f"Available Routes:<br/>"
        f"- Precipitation Data: /api/v1.0/precipitation<br/>"
        f"- Station Data: /api/v1.0/stations<br/>"
        f"- Temperature Data: /api/v1.0/tobs<br/>"
        f"- Search by Start Date: /api/v1.0/YYYY-MM-DD<br/>"
        f"- Search Date Range: /api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    last_year_prcp = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_dict = {}
    for date, prcp in last_year_prcp: 
        prcp_dict[date]=prcp

    #Return the JSON representation of your dictionary.
    return jsonify (prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    session = Session(engine)
    station_count = session.query(Station.station).all()
    session.close()
    station_list= []
    for station in station_count: 
        station_list.append(station[0])
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    session = Session(engine)
    last_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').filter(Measurement.date>=last_year_date).all()
    session.close()
    tobs_list= []
    for tobs in most_active_station: 
        tobs_list.append(tobs[0])

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_list)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")
def start(start):
    try: 
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        session = Session(engine)
        station_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()
        session.close()
        summary_dict = {}
        summary_dict["Input Date"] = start
        summary_dict["TMIN"] = station_stats[0][0]
        summary_dict["TMAX"] = station_stats[0][1]
        summary_dict["TAVG"] = station_stats[0][2]

        return jsonify(summary_dict)
    except: 
        return jsonify({"error": f"Invalid Date Format. Please enter date in yyyy-mm-dd format."}), 404

#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
        session = Session(engine)
        date_range = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date.between(start_date, end_date)).all()
        session.close()
        summary_dict = {}
        summary_dict["Start Date"] = start
        summary_dict["End Date"] = end
        summary_dict["TMIN"] = date_range[0][0]
        summary_dict["TMAX"] = date_range[0][1]
        summary_dict["TAVG"] = date_range[0][2]

        return jsonify(summary_dict)
    except: 
        return jsonify({"error": f"Invalid Date Format. Please enter date in yyyy-mm-dd format."}), 404

if __name__ == "__main__":
    app.run()