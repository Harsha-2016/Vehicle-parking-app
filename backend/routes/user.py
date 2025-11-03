# backend/routes/user.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from datetime import datetime
import math
from sqlalchemy import func

# Import your models & db object the same way your admin file does.
# If you used a models aggregator `backend.models.models`, import from there;
# otherwise import individually. Adjust this import to match your project.
from models.db_setup import db
from models.User import User
from models.ParkingLot import ParkingLot
from models.ParkingSpot import ParkingSpot
from models.Reservation import Reservation

user_bp = Blueprint("user_bp", __name__)

def check_user():
    user_id = get_jwt_identity()
    claims = get_jwt()
    if claims.get("role") != "user":
        return jsonify({"msg": "User access required"}), 403
    return int(user_id),None

# -----------------------------
# Get available parking lots (summary)
# -----------------------------
@user_bp.route("/lots", methods=["GET"])
@jwt_required()
def get_lots():
    # Any logged-in user (admin or user) can view lots.
    lots = ParkingLot.query.all()
    result = []
    for lot in lots:
        total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
        occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status="O").count()
        available = total_spots - occupied
        result.append({
            "lot_id": lot.id,
            "prime_location_name": lot.prime_location_name,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "price": lot.price_per_hour,
            "total_spots": total_spots,
            "available_spots": available,
            "occupied_spots": occupied
        })
    return jsonify(result), 200


# -----------------------------
# Reserve: auto-allocate first available spot in a lot
# Body: { "lot_id": <int> }
# -----------------------------
@user_bp.route("/reserve", methods=["POST"])
@jwt_required()
def reserve_spot():
    user_id,error=check_user()
    if error:
        return error

    data = request.get_json()
    lot_id = data.get("lot_id")
    if not lot_id:
        return jsonify({"error": "lot_id required"}), 400

    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"error": "Parking lot not found"}), 404

    # find first available spot
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status="A").first()
    if not spot:
        return jsonify({"error": "No available spots in this lot"}), 409

    # create reservation and mark spot occupied
    try:
        spot.status = "O"
        reservation = Reservation(
            spot_id=spot.id,
            user_id=user_id,
            parking_timestamp=datetime.utcnow(),
            leaving_timestamp=None,
            parking_cost=0.0
        )
        db.session.add(reservation)
        db.session.commit()

        return jsonify({
            "message": "Spot reserved",
            "reservation_id": reservation.id,
            "spot_id": spot.id,
            "parking_timestamp": reservation.parking_timestamp.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to reserve spot", "detail": str(e)}), 500


# -----------------------------
# Occupy a spot (explicit action)
# Some flows auto-mark occupied at reservation time; this endpoint
# can serve if you require explicit "I parked now" action.
# Body: { "reservation_id": <int> }
# -----------------------------
@user_bp.route("/occupy", methods=["POST"])
@jwt_required()
def occupy_spot():
    user_id,error=check_user()
    if error:
        return error
    data = request.get_json()
    res_id = data.get("reservation_id")
    if not res_id:
        return jsonify({"error": "reservation_id required"}), 400

    reservation = Reservation.query.get(res_id)
    if not reservation or reservation.user_id != user_id:
        return jsonify({"error": "Reservation not found"}), 404

    # If someone reserved but didn't set status, we mark parking_timestamp now.
    if reservation.parking_timestamp is None:
        reservation.parking_timestamp = datetime.utcnow()

    # Also ensure spot is marked 'O'
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = "O"
    db.session.commit()

    return jsonify({"message": "Spot occupied", "spot_id": spot.id}), 200


# -----------------------------
# Release a spot (end parking)
# Path param option OR body: { "reservation_id": <int> }
# We use body here.
# -----------------------------
@user_bp.route("/release", methods=["POST"])
@jwt_required()
def release_spot():
    user_id,error=check_user()
    if error:
        return error
    
   # print("DEBUG occupy_spot called by user_id:", user_id,type(user_id))
    data = request.get_json()
    #print("DEBUG Incoming data:", data) 
    res_id = data.get("reservation_id")
    if not res_id:
        return jsonify({"error": "reservation_id required"}), 400

    reservation = Reservation.query.get(res_id)
    #print("DEBUG user_id:", user_id, "res_id:", reservation)
    #print("DEBUG reservation details:", reservation.user_id,type(reservation.user_id) if reservation else "N/A")
    if (reservation==None) :
        return jsonify({"error": "Reservation not found 1" }), 404
    if( reservation.user_id != user_id):
        return jsonify({"error": "Reservation not found 2"}), 404

    if reservation.leaving_timestamp is not None:
        return jsonify({"error": "Reservation already released"}), 400

    reservation.leaving_timestamp = datetime.utcnow()

    # compute cost:
    lot = ParkingLot.query.join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)\
                          .filter(ParkingSpot.id == reservation.spot_id).first()
    if not lot:
        # fallback: query via spot
        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)

    # calculate duration in seconds
    duration_sec = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds()
    #print("DEBUG Parking duration (sec):", duration_sec)
    # Bill per hour — round up to next whole hour
    hours = math.ceil(duration_sec / 3600) if duration_sec > 0 else 0
    #print("DEBUG Parking duration (hours):", hours)
    cost = hours * float(lot.price_per_hour)

    reservation.parking_cost = cost

    # mark spot available
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = "A"

    db.session.commit()

    return jsonify({
        "message": "Spot released",
        "reservation_id": reservation.id,
        "parking_cost": cost,
        "hours_charged": hours
    }), 200


# -----------------------------
# User reservation history
# -----------------------------
@user_bp.route("/me/reservations", methods=["GET"])
@jwt_required()
def my_reservations():
    user_id,error=check_user()
    if error:
        return error

    user_id = user_id
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.parking_timestamp.desc()).all()
    data = []
    for r in reservations:
        duration_str = None
        if r.leaving_timestamp and r.parking_timestamp:
            duration = r.leaving_timestamp - r.parking_timestamp
            total_minutes = int(duration.total_seconds() // 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            duration_str = f"{hours} hrs {minutes} mins"

        spot = ParkingSpot.query.get(r.spot_id)
        lot = ParkingLot.query.get(spot.lot_id) if spot else None

        data.append({
            "reservation_id": r.id,
            "spot_id": r.spot_id,
            "lot_id": lot.id if lot else None,
            "lot_name": lot.prime_location_name if lot else None,
            "parking_timestamp": r.parking_timestamp.isoformat() if r.parking_timestamp else None,
            "leaving_timestamp": r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
            "parking_cost": r.parking_cost,
            "duration": duration_str
        })
    return jsonify(data), 200

# -----------------------------
# User analytics
# -----------------------------
@user_bp.route("/analytics", methods=["GET"])
@jwt_required()
def user_analytics():
    # validate user and extract id
    user_id, error = check_user()        # your check_user returns (user_id, None) or (None, error)
    if error:
        return error

    try:
        # Only include reservations that have a leaving_timestamp (completed sessions)
        # Use SQLite julianday to compute duration hours: (julianday(leaving)-julianday(start)) * 24
        q = (
            db.session.query(
                func.strftime("%Y-%m", Reservation.parking_timestamp).label("month"),
                func.coalesce(func.sum((func.julianday(Reservation.leaving_timestamp) - func.julianday(Reservation.parking_timestamp)) * 24), 0).label("total_hours"),
                func.coalesce(func.sum(Reservation.parking_cost), 0).label("total_amount")
            )
            .filter(Reservation.user_id == user_id)
            .filter(Reservation.parking_timestamp != None)
            .filter(Reservation.leaving_timestamp != None)
            .group_by("month")
            .order_by("month")
        )

        rows = q.all()

        # Build arrays for charts (month labels, hours and amount)
        parking_stats = []
        revenue_stats = []

        for r in rows:
            month = r.month  # e.g. "2025-10"
            total_hours = float(r.total_hours) if r.total_hours is not None else 0.0
            total_amount = float(r.total_amount) if r.total_amount is not None else 0.0

            parking_stats.append({"month": month, "hours": round(total_hours, 2)})
            revenue_stats.append({"month": month, "amount": round(total_amount, 2)})

        # Also compute totals
        total_hours_all = sum(p["hours"] for p in parking_stats)
        total_spent_all = sum(r["amount"] for r in revenue_stats)

        return jsonify({
            "parkingStats": parking_stats,
            "revenueStats": revenue_stats,
            "total_hours": round(total_hours_all,2),
            "total_spent": round(total_spent_all,2)
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Error in user_analytics:", e)
        return jsonify({"error": "Internal server error"}), 500
    


