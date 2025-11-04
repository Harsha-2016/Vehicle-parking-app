# backend/models/ParkingSpot.py
from .db_setup import db

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(1), default="A")  # A = Available, O = Occupied

    reservation = db.relationship("Reservation", backref="spot", lazy=True, uselist=False)

    
