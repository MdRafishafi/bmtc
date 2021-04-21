from app import app, db

from flask import request
from sqlalchemy import and_
from app import  bus_stops_database as bsd, generate_ids as gids

LATITUDE = 0.00090053582
LONGITUDE = 0.00113804251


@app.route('/bmtc/add/new/bus-stop', methods=["POST"])
def bmtc_add():
    uid = gids.generate_id(bsd.BusStops)
    bus_stop = request.form.get('bus_stop')
    lat = request.form.get('lat')
    long = request.form.get('long')
    result = bsd.BusStops.query.filter_by(latitude=lat, longitude=long).first()
    if result:
        return {
            "error": 300,
            "message": "bus stop already exist"
        }
    else:
        bus_stop_data = bsd.BusStops(
            id=uid,
            bus_stop=bus_stop,
            latitude=float(lat),
            longitude=float(long),
        )
        db.session.add(bus_stop_data)
        db.session.commit()
    return {
        "id": uid,
        "bus_stop": bus_stop,
        "lat": lat,
        "long": long
    }


@app.route('/bmtc/search/bus-stop/<bus_stop_id>', methods=["GET"])
def bmtc_get_bus_id(bus_stop_id):
    results: bsd.BusStops = bsd.BusStops.query.filter_by(id=bus_stop_id).all()
    return {
        "id": results.id,
        "bus_stop_name": results.bus_stop,
        "latitude": results.latitude,
        "longitude": results.longitude
    }


@app.route('/bmtc/search/bus-stop/by-starting-letter/<starting_letter>', methods=["GET"])
def bmtc_get_all_bus_stops(starting_letter):
    bus_route = db.session.query(bsd.BusStops.id, bsd.BusStops.bus_stop).all()
    all_route_no = []
    for data in bus_route:
        if str(data[1]).lower().startswith(starting_letter):
            all_route_no.append({"id": data[0], "bus_stop": data[1]})
    return {
        "bus_stops": all_route_no
    }


@app.route('/bmtc/delete/<bus_stop_id>', methods=["DELETE"])
def bmtc_delete(bus_stop_id):
    bsd.BusStops.query.filter_by(id=bus_stop_id).delete()
    db.session.commit()
    return {
        "result": "delete successfully"
    }


@app.route('/bmtc/<lat>/<long>', methods=["GET"])
def bmtc_bus_stops(lat, long):
    radius = 1
    all_near_by_bus_stop = []
    while len(all_near_by_bus_stop) < 10:
        all_near_by_bus_stop = []
        radius += 1
        up_lim_lat = float(lat) + LATITUDE * radius
        up_lim_long = float(long) + LONGITUDE * radius
        lower_lim_lat = float(lat) - LATITUDE * radius
        lower_lim_long = float(long) - LONGITUDE * radius
        result = bsd.BusStops.query.filter(and_(
            lower_lim_lat <= bsd.BusStops.latitude,
            up_lim_lat >= bsd.BusStops.latitude,
            lower_lim_long <= bsd.BusStops.longitude,
            up_lim_long >= bsd.BusStops.longitude
        )).all()
        for data in result:
            temp = {"id": data.id, "bus_stop_name": data.bus_stop, "latitude": data.latitude,
                    "longitude": data.longitude}
            all_near_by_bus_stop.append(temp)

    return {
        "radius": radius * 100,
        "bus_stops": all_near_by_bus_stop
    }
