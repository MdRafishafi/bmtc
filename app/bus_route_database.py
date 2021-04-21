from app import db


class BusRoute(db.Model):
    __tablename__ = 'BusRoute'
    id = db.Column(db.String(32), primary_key=True)
    bus_no = db.Column(db.String(20), nullable=False)
    distance = db.Column(db.String(10), nullable=False)
    list_of_bus_stops = db.Column(db.JSON(), nullable=False)
