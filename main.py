import uuid
from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///mybmtc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

LATITUDE = 0.00090053582
LONGITUDE = 0.00113804251


class BusStops(db.Model):
    __tablename__ = 'BusStops'
    id = db.Column(db.String(100), primary_key=True)
    bus_stop = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)


db.create_all()


def generate_id(table_data: db.Model):
    uid = str(uuid.uuid4()).replace('-', '')
    result = table_data.query.filter_by(id=uid).first()
    if not result:
        return uid
    else:
        generate_id(table_data)


@app.route('/bmtc/add/<bus_stop>/<lat>/<long>', methods=["POST"])
def bmtc_add(bus_stop, lat, long):
    uid = generate_id(BusStops)
    bus_stop_data = BusStops(
        id=uid,
        bus_stop=bus_stop,
        latitude=float(lat),
        longitude=float(long),
    )
    db.session.add(bus_stop_data)
    db.session.commit()
    return {
        "result": True
    }


@app.route('/bmtc/delete/<bus_stop_id>', methods=["POST"])
def bmtc_delete(bus_stop_id):
    BusStops.query.delete_by(id=bus_stop_id)
    db.session.commit()
    return {
        "result": True
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
        "result": "MY BMTC"
    }


if __name__ == "__main__":
    app.run(debug=True)
