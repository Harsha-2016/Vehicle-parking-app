# backend/models/ParkingLot.py
from .db_setup import db

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(120), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255))
    pin_code = db.Column(db.String(10))
    number_of_spots = db.Column(db.Integer, nullable=False)

    spots = db.relationship("ParkingSpot", backref="lot", lazy=True)

    
