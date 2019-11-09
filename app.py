import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    prcp_query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>year_ago).\
        order_by(Measurement.date.desc()).all()

    session.close()

    prcp_list = []
    for date, prcp in prcp_query:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)
@app.route("/api/v1.0/station")
def stations():
    session = Session(engine)

    st = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(st))
    return jsonify(all_stations)
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    count=func.count(Measurement.station)

    most_active = session.query(Measurement.station,count).\
        group_by(Measurement.station).\
        order_by(count.desc()).first()

    tobs_yr_ago = dt.date(2017,8,18) - dt.timedelta(days=365)
    tobs_query = session.query(Measurement.tobs).\
        filter(Measurement.date>tobs_yr_ago).\
        filter(Measurement.station == most_active[0]).all()

    session.close()

    yr_ago_tobs = list(np.ravel(tobs_query))
    return jsonify(yr_ago_tobs)

@app.route("/api/v1.0/<start>")
def stats1(start):
    session = Session(engine)
    low_temp = func.min(Measurement.tobs)
    high_temp = func.max(Measurement.tobs)
    avg_temp = func.avg(Measurement.tobs)

    sel = [low_temp, high_temp, avg_temp]

    first_query = session.query(*sel).\
        filter(Measurement.date >= start).all()
    
    session.close()

    calc_stat1 = list(np.ravel(first_query))
    return jsonify(calc_stat1)
    
@app.route("/api/v1.0/<start>/<end>")
def stats2(start,end):
    session = Session(engine)
    low_temp = func.min(Measurement.tobs)
    high_temp = func.max(Measurement.tobs)
    avg_temp = func.avg(Measurement.tobs)

    sel = [low_temp, high_temp, avg_temp]

    second_query = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    calc_stat2 = list(np.ravel(second_query))
    return jsonify(calc_stat2)
    
if __name__ == '__main__':
    app.run(debug=True)
