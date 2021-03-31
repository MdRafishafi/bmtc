import uuid
from os import environ
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///mybmtc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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


@app.route('/bmtc/add/<bus_stop>/<lat>/<long>', methods=["GET"])
def bmtc_add(bus_stop, lat, long):
    uid = generate_id(BusStops)
    bus_stop_data = BusStops(id=uid,
                             bus_stop=bus_stop,
                             latitude=float(lat),
                             longitude=float(long),
                             )
    db.session.add(bus_stop_data)
    db.session.commit()
    return {
        "result": True
    }


@app.route('/', methods=["GET"])
def home():
    return {
        "result": "MY BMTC"
    }


if __name__ == "__main__":
    app.run()
