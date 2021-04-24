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
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    result = bsd.BusStops.query.filter_by(latitude=latitude, longitude=longitude).first()
    if result:
        return {
                   "message": "bus stop already exist"
               }, 409
    else:
        bus_stop_data = bsd.BusStops(
            id=uid,
            bus_stop=bus_stop,
            latitude=float(latitude),
            longitude=float(longitude),
        )
        db.session.add(bus_stop_data)
        db.session.commit()
    return {
        "id": uid,
        "bus_stop": bus_stop,
        "latitude": latitude,
        "longitude": longitude
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
        "latitude": result.latitude,
        "longitude": result.longitude
    }


@app.route('/bmtc/search/bus-stop/by-starting-letter/<starting_letter>', methods=["GET"])
def bmtc_get_all_bus_stops(starting_letter: str):
    bus_route = db.session.query(bsd.BusStops).all()
    if not bus_route:
        return {
                   "message": f"Bus Stop Starting with {starting_letter} letter is not found"
               }, 404
    all_route_no = []
    data: bsd.BusStops
    for data in bus_route:
        if str(data.bus_stop).lower().startswith(starting_letter.lower()):
            all_route_no.append({"id": data.id, "bus_stop": data.bus_stop, "latitude": data.latitude, "longitude": data.longitude})
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


@app.route('/bmtc/<latitude>/<longitude>', methods=["GET"])
def bmtc_bus_stops(latitude, longitude):
    try:
        radius = 1
        all_near_by_bus_stop = []
        while len(all_near_by_bus_stop) < 10:
            all_near_by_bus_stop = []
            radius += 1
            up_lim_latitude = float(latitude) + LATITUDE * radius
            up_lim_longitude = float(longitude) + LONGITUDE * radius
            lower_lim_latitude = float(latitude) - LATITUDE * radius
            lower_lim_longitude = float(longitude) - LONGITUDE * radius
            result = bsd.BusStops.query.filter(and_(
                lower_lim_latitude <= bsd.BusStops.latitude,
                up_lim_latitude >= bsd.BusStops.latitude,
                lower_lim_longitude <= bsd.BusStops.longitude,
                up_lim_longitude >= bsd.BusStops.longitude
            )).all()
            for data in result:
                all_near_by_bus_stop.append({"id": data.id, "bus_stop": data.bus_stop, "latitude": data.latitude,
                                             "longitude": data.longitude})

        return {
            "list_of_bus_stops": all_near_by_bus_stop
        }
    except:
        return {
                   "message": "There are no Bus Stops near by you"
               }, 404
