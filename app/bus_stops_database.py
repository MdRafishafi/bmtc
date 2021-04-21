from app import db


class BusStops(db.Model):
    __tablename__ = 'BusStops'
    id = db.Column(db.String(32), primary_key=True)
    bus_stop = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
