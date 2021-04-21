from app import app, db

from flask import request
from sqlalchemy import and_
from app import bus_stops_database as bsd, generate_ids as gids

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
                   "message": "bus stop already exist"
               }, 409
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
    result: bsd.BusStops = bsd.BusStops.query.filter_by(id=bus_stop_id).all()
    if not result:
        return {
                   "message": "Bus stop is not found"
               }, 404
    return {
        "id": result.id,
        "bus_stop": result.bus_stop,
        "lat": result.latitude,
        "long": result.longitude
    }


@app.route('/bmtc/search/bus-stop/by-starting-letter/<str: starting_letter>', methods=["GET"])
def bmtc_get_all_bus_stops(starting_letter: str):
    bus_route = db.session.query.all()
    if not bus_route:
        return {
                   "message": f"Bus Stop Starting with {starting_letter} letter is not found"
               }, 404
    all_route_no = []
    data: bsd.BusStops
    for data in bus_route:
        if str(data.bus_stop).lower().startswith(starting_letter.lower()):
            all_route_no.append({"id": data.id, "bus_stop": data.bus_stop, "lat": data.latitude, "long": data.longitude})
    return {
        "list_of_bus_stops": all_route_no
    }


@app.route('/bmtc/delete/<bus_stop_id>', methods=["DELETE"])
def bmtc_delete(bus_stop_id):
    try:
        bsd.BusStops.query.filter_by(id=bus_stop_id).delete()
        db.session.commit()
        return {
            "message": "delete successfully"
        }
    except:
        return {
                   "message": "Bus stop is not found"
               }, 404


@app.route('/bmtc/<lat>/<long>', methods=["GET"])
def bmtc_bus_stops(lat, long):
    try:
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
                all_near_by_bus_stop.append({"id": data.id, "bus_stop_name": data.bus_stop, "latitude": data.latitude,
                                             "longitude": data.longitude})

        return {
            "list_of_bus_stops": all_near_by_bus_stop
        }
    except:
        return {
                   "message": "There are no Bus Stops near by you"
               }, 404
