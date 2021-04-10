import uuid
from os import environ
import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, ForeignKey
from geopy.distance import geodesic

app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///mybmtc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

LATITUDE = 0.00090053582
LONGITUDE = 0.00113804251


class BusStops(db.Model):
    __tablename__ = 'BusStops'
    id = db.Column(db.String(100), primary_key=True)
    bus_stop = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)


class BusRoute(db.Model):
    __tablename__ = 'BusRoute'
    id = db.Column(db.String(100), primary_key=True)
    bus_no = db.Column(db.String(20), nullable=False)
    distance = db.Column(db.String(10), nullable=False)
    list_of_bus_stops = db.Column(db.JSON(), nullable=False)


db.create_all()


def generate_id(table_data: db.Model):
    uid = str(uuid.uuid4()).replace('-', '')
    result = table_data.query.filter_by(id=uid).first()
    if not result:
        return uid
    else:
        generate_id(table_data)


@app.route('/bmtc/add/new/bus-stop', methods=["POST"])
def bmtc_add():
    uid = generate_id(BusStops)
    bus_stop = request.form.get('bus_stop')
    lat = request.form.get('lat')
    long = request.form.get('long')
    result = BusStops.query.filter_by(latitude=lat, longitude=long).first()
    if result:
        return {
            "error": 300,
            "message": "bus stop already exist"
        }
    else:
        bus_stop_data = BusStops(
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


@app.route('/bmtc/add/new/bus-route', methods=["POST"])
def bmtc_add_bus_route():
    bus_no = request.form.get('bus_no')
    list_of_bus_stops_name = json.loads(request.form.get('list_of_bus_stops'))
    distance = request.form.get('distance')
    result = BusRoute.query.filter_by(bus_no=bus_no).first()
    if result:
        return {
            "error": 300,
            "message": "bus stop already exist"
        }
    else:
        list_of_bus_stops = []
        for bus_stop in list_of_bus_stops_name:
            bus_stop_result = BusStops.query.filter_by(bus_stop=bus_stop).first()
            if bus_stop_result:
                list_of_bus_stops.append({"bus_stop_id": bus_stop_result.id})
            else:
                return {
                    "error": 300,
                    "message": f"{bus_stop} do not exist in Bus Stop list"
                }
        for index in range(len(list_of_bus_stops) - 1):
            bus_point_1: BusStops = BusStops.query.filter_by(id=list_of_bus_stops[index]["bus_stop_id"]).first()
            bus_point_2: BusStops = BusStops.query.filter_by(id=list_of_bus_stops[index + 1]["bus_stop_id"]).first()
            coords_1 = (bus_point_1.latitude, bus_point_1.latitude)
            coords_2 = (bus_point_2.latitude, bus_point_2.latitude)
            if index == 0:
                coords_start = coords_1
            if index + 1 == len(list_of_bus_stops) - 1:
                coords_end = coords_2
            list_of_bus_stops[index + 1]["distance"] = f"{round(geodesic(coords_1, coords_2).km, 4)} M"
        uid = generate_id(BusRoute)
        user_data = BusRoute(
            id=uid,
            bus_no=bus_no,
            list_of_bus_stops=list_of_bus_stops,
            distance=distance if distance else f"{round(geodesic(coords_start, coords_end).km, 3)} KM"
        )
        db.session.add(user_data)
        db.session.commit()
    return {
        "bus_route_id": uid,
    }


@app.route('/bmtc/search/bus-stop/<bus_stop_id>', methods=["GET"])
def bmtc_get_bus_id(bus_stop_id):
    results: BusStops = BusStops.query.filter_by(id=bus_stop_id).all()
    return {
        "id": results.id,
        "bus_stop_name": results.bus_stop,
        "latitude": results.latitude,
        "longitude": results.longitude
    }


@app.route('/bmtc/search/bus-route-no/<bus_route_no_id>', methods=["GET"])
def bmtc_get_bus_route_by_bus_no(bus_route_no_id):
    bus_route: BusRoute = BusRoute.query.filter_by(id=bus_route_no_id).first()
    list_of_bus_stops = []
    for bus_stop_data in json.loads(bus_route.list_of_bus_stops):
        bus_stop: BusStops = BusStops.query.filter_by(id=bus_stop_data).first()
        list_of_bus_stops.append({
            "id": bus_stop.id,
            "bus_stop_name": bus_stop.bus_stop,
            "latitude": bus_stop.latitude,
            "longitude": bus_stop.longitude
        })
    return {
        "id": bus_route.id,
        "bus_route_no": bus_route.bus_no,
        "bus_stops": list_of_bus_stops
    }


@app.route('/bmtc/search/bus-route/by-starting-letter/<starting_letter>', methods=["GET"])
def bmtc_get_all_bus_route_no(starting_letter):
    bus_route = db.session.query(BusRoute.id, BusRoute.bus_no).all()
    all_route_no = []
    for data in bus_route:
        if str(data[1]).lower().startswith(starting_letter):
            all_route_no.append({"id": data[0], "bus_route_no": data[1]})
    return {
        "bus_route_no": all_route_no
    }


@app.route('/bmtc/search/bus-stop/by-starting-letter/<starting_letter>', methods=["GET"])
def bmtc_get_all_bus_stops(starting_letter):
    bus_route = db.session.query(BusStops.id, BusStops.bus_stop).all()
    all_route_no = []
    for data in bus_route:
        if str(data[1]).lower().startswith(starting_letter):
            all_route_no.append({"id": data[0], "bus_route_no": data[1]})
    return {
        "bus_stops": all_route_no
    }


@app.route('/bmtc/delete/<bus_stop_id>', methods=["DELETE"])
def bmtc_delete(bus_stop_id):
    BusStops.query.filter_by(id=bus_stop_id).delete()
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
        result = BusStops.query.filter(and_(
            lower_lim_lat <= BusStops.latitude,
            up_lim_lat >= BusStops.latitude,
            lower_lim_long <= BusStops.longitude,
            up_lim_long >= BusStops.longitude
        )).all()
        for data in result:
            temp = {"id": data.id, "bus_stop_name": data.bus_stop, "latitude": data.latitude,
                    "longitude": data.longitude}
            all_near_by_bus_stop.append(temp)

    return {
        "radius": radius * 100,
        "bus_stops": all_near_by_bus_stop
    }


@app.route('/', methods=["GET"])
def home():
    return {
        "Application": "MY BMTC"
    }


if __name__ == "__main__":
    app.run()
