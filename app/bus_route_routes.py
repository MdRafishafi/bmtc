from app import app, db, bus_route_database as brd, generate_ids as gids, bus_stops_database as bsd
import json

from flask import request
from geopy.distance import geodesic


@app.route('/bmtc/add/new/bus-route', methods=["POST"])
def bmtc_add_bus_route():
    bus_no = request.form.get('bus_no')
    list_of_bus_stops_name = json.loads(request.form.get('list_of_bus_stops'))
    distance = request.form.get('distance')
    result = db.session.query(brd.BusRoute.id).filter_by(bus_no=bus_no).first()
    if result:
        return {
            "message": "bus stop already exist"
        }, 409
    else:
        list_of_bus_stops = []
        for bus_stop in list_of_bus_stops_name:
            bus_stop_result = bsd.BusStops.query.filter_by(bus_stop=bus_stop).first()
            if bus_stop_result:
                list_of_bus_stops.append({"bus_stop_id": bus_stop_result.id})
            else:
                return {
                    "message": f"{bus_stop} do not exist in Bus Stop list"
                }, 404
        for index in range(len(list_of_bus_stops) - 1):
            bus_point_1: bsd.BusStops = bsd.BusStops.query.filter_by(id=list_of_bus_stops[index]["bus_stop_id"]).first()
            bus_point_2: bsd.BusStops = bsd.BusStops.query.filter_by(
                id=list_of_bus_stops[index + 1]["bus_stop_id"]).first()
            coords_1 = (bus_point_1.latitude, bus_point_1.longitude)
            coords_2 = (bus_point_2.latitude, bus_point_2.longitude)
            if index == 0:
                coords_start = coords_1
            if index + 1 == len(list_of_bus_stops) - 1:
                coords_end = coords_2
            list_of_bus_stops[index + 1]["distance"] = f"{round(geodesic(coords_1, coords_2).km, 4)} M"
        uid = gids.generate_id(brd.BusRoute)
        user_data = brd.BusRoute(
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


@app.route('/bmtc/search/bus-route-no/<bus_route_no_id>', methods=["GET"])
def bmtc_get_bus_route_by_bus_no(bus_route_no_id):
    bus_route: brd.BusRoute = brd.BusRoute.query.filter_by(id=bus_route_no_id).first()
    if not bus_route:
        return {
            "message": "Bus Route is not found"
        }, 404
    list_of_bus_stops = []
    for bus_stop_data in bus_route.list_of_bus_stops:
        bus_stop: bsd.BusStops = bsd.BusStops.query.filter_by(id=bus_stop_data["id"]).first()
        temp = {
            "id": bus_stop.id,
            "bus_stop_name": bus_stop.bus_stop,
            "latitude": bus_stop.latitude,
            "longitude": bus_stop.longitude
        }
        if "distance" in bus_stop_data.keys():
            temp["distance"] = bus_stop_data["distance"]
        list_of_bus_stops.append(temp)
    return {
        "id": bus_route.id,
        "bus_no": bus_route.bus_no,
        "list_of_bus_stops": list_of_bus_stops
    }


@app.route('/bmtc/search/bus-route/by-starting-letter/<starting_letter>', methods=["GET"])
def bmtc_get_all_bus_route_no(starting_letter):
    bus_route = db.session.query(brd.BusRoute.id, brd.BusRoute.bus_no).all()
    all_route_no = []
    for data in bus_route:
        if str(data[1]).lower().startswith(starting_letter):
            all_route_no.append({"id": data[0], "bus_route_no": data[1]})
    return {
        "list_of_bus_no": all_route_no
    }
