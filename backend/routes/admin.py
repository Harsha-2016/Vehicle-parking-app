from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.db_setup import db
from models.User import User
from models.ParkingLot import ParkingLot
from models.ParkingSpot import ParkingSpot
from models.Reservation import Reservation
from datetime import datetime
from sqlalchemy import func
from extensions import cache

admin_bp = Blueprint("admin_bp", __name__)


# ------------------------------------------------------------
# 🧩 Utility: Check if current user is admin
# ------------------------------------------------------------
def check_admin():
    user_id = get_jwt_identity()
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"msg": "Admin access required"}), 403
    return None


# ------------------------------------------------------------
# ✅ Create Parking Lot
# ------------------------------------------------------------
@admin_bp.route('/create_lot', methods=['POST'])
@jwt_required()
def create_parking_lot():
    check = check_admin()
    if check:
        return check

    data = request.get_json()
    print("Received data for new parking lot:", data)
    required_fields = ['prime_location_name', 'price_per_hour', 'address', 'pin_code', 'number_of_spots']

    # Validate required fields
    for field in required_fields:
        if field not in data or str(data[field]).strip() == "":
            return jsonify({"error": f"Missing or invalid field: {field}"}), 400

    try:
        price_per_hour = float(data['price_per_hour'])
        number_of_spots = int(data['number_of_spots'])

        new_lot = ParkingLot(
            prime_location_name=data['prime_location_name'].strip(),
            price_per_hour=price_per_hour,
            address=data['address'].strip(),
            pin_code=data['pin_code'].strip(),
            number_of_spots=number_of_spots
        )
        db.session.add(new_lot)
        db.session.commit()

        # Create parking spots
        for i in range(number_of_spots):
            spot = ParkingSpot(lot_id=new_lot.id, status="A")
            db.session.add(spot)
        db.session.commit()

        return jsonify({
            "message": "Parking lot created successfully!",
            "lot": {
                "id": new_lot.id,
                "prime_location_name": new_lot.prime_location_name,
                "price_per_hour": new_lot.price_per_hour,
                "address": new_lot.address,
                "pin_code": new_lot.pin_code,
                "number_of_spots": new_lot.number_of_spots
            }
        }), 201

    except ValueError:
        return jsonify({"error": "Invalid numeric value for price_per_hour or number_of_spots"}), 400

    except Exception as e:
        db.session.rollback()
        print("❌ Error creating parking lot:", e)
        return jsonify({"error": "Internal server error"}), 500


# ------------------------------------------------------------
# 🔄 Update Parking Lot
# ------------------------------------------------------------
@admin_bp.route("/update_lot/<int:lot_id>", methods=["PUT"])
@jwt_required()
def update_parking_lot(lot_id):
    check = check_admin()
    if check:
        return check

    data = request.get_json()
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404

    try:
        lot.prime_location_name = data.get("prime_location_name", lot.prime_location_name)
        lot.price_per_hour = float(data.get("price_per_hour", lot.price_per_hour))
        lot.address = data.get("address", lot.address)
        lot.pin_code = data.get("pin_code", lot.pin_code)
        if int(data.get("number_of_spots", lot.number_of_spots)) > lot.number_of_spots:
            difference = int(data["number_of_spots"]) - lot.number_of_spots
            for _ in range(difference):
                new_spot = ParkingSpot(lot_id=lot.id, status="A")  # Available
                db.session.add(new_spot)
        # If total spots decreased, remove excess available spots
        elif int(data.get("number_of_spots", lot.number_of_spots)) < lot.number_of_spots:
            difference = lot.number_of_spots - int(data["number_of_spots"])
            spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot.id, status="A").limit(difference).all()
            for s in spots_to_remove:
                db.session.delete(s)

        lot.number_of_spots = int(data["number_of_spots"])
        db.session.commit()
        return jsonify({"message": "Parking lot updated successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        print("❌ Error updating lot:", e)
        return jsonify({"error": "Internal server error"}), 500


# ------------------------------------------------------------
# 🗑️ Delete Parking Lot (only if all spots are empty)
# ------------------------------------------------------------
@admin_bp.route("/delete_lot/<int:lot_id>", methods=["DELETE"])
@jwt_required()
def delete_parking_lot(lot_id):
    check = check_admin()
    if check:
        return check

    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"error": "Lot not found"}), 404

    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status="O").count()
    if occupied_spots > 0:
        return jsonify({"error": "Cannot delete lot with occupied spots"}), 400

    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()

    return jsonify({"message": "Parking lot deleted successfully"}), 200


# ------------------------------------------------------------
# 📊 View All Parking Lots (with spot summary)
# ------------------------------------------------------------
@admin_bp.route("/lots", methods=["GET"])
@jwt_required()
def view_parking_lots():
    check = check_admin()
    if check:
        return check

    lots = ParkingLot.query.all()
    result = []
    for lot in lots:
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        available = sum(1 for s in spots if s.status == "A")
        occupied = sum(1 for s in spots if s.status == "O")
        result.append({
            "id": lot.id,
            "prime_location_name": lot.prime_location_name,
            "price_per_hour": lot.price_per_hour,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "number_of_spots": lot.number_of_spots,
            "available_spots": available,
            "occupied_spots": occupied
        })
    print(result)
    return jsonify(result), 200


# ------------------------------------------------------------
# 🚗 View Spot Details per Lot
# ------------------------------------------------------------
@admin_bp.route("/lot/<int:lot_id>/spots", methods=["GET"])
@jwt_required()
def view_spots(lot_id):
    check = check_admin()
    if check:
        return check

    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    if not spots:
        return jsonify({"error": "No spots found"}), 404

    result = []
    for spot in spots:
        reservation = Reservation.query.filter_by(spot_id=spot.id).order_by(Reservation.parking_timestamp.desc()).first()
        user_details = None
        if reservation and reservation.leaving_timestamp is None:
            user_obj = User.query.get(reservation.user_id)
            if user_obj:
                user_details = {
                    "username": user_obj.username,
                    "user_id": user_obj.id,
                    "parking_timestamp": reservation.parking_timestamp
                }
        result.append({
            "spot_id": spot.id,
            "status": spot.status,
            "user_details": user_details
        })
    return jsonify(result), 200


# ------------------------------------------------------------
# 👥 View All Users
# ------------------------------------------------------------
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def view_all_users():
    check = check_admin()
    if check:
        return check

    users = User.query.filter_by(role="user").all()
    result = []
    for u in users:
        active_reservation = Reservation.query.filter_by(user_id=u.id, leaving_timestamp=None).first()
        spot_id = active_reservation.spot_id if active_reservation else None
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "active_spot": spot_id
        })
        print("User fetched:", u.email, "Active spot:", spot_id)
    return jsonify(result), 200


# ------------------------------------------------------------
# Admin view: All reservations
# ------------------------------------------------------------
@admin_bp.route("/reservations", methods=["GET"])
@jwt_required()
@cache.cached(timeout=180)
def view_all_reservations():
    check = check_admin()
    if check:
        return check

    reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).all()
    result = []
    for res in reservations:
        duration_str = None
        if res.leaving_timestamp and res.parking_timestamp:
            duration = res.leaving_timestamp - res.parking_timestamp
            total_minutes = int(duration.total_seconds() // 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            duration_str = f"{hours} hrs {minutes} mins"

        user = User.query.get(res.user_id)
        spot = ParkingSpot.query.get(res.spot_id)
        lot = ParkingLot.query.get(spot.lot_id) if spot else None
            
        result.append({
            "reservation_id": res.id,
            "user_name": user.username if user else None,
            "lot_name": lot.prime_location_name if lot else None,
            "spot_id": res.spot_id,
            "lot_id": lot.id if lot else None,
            "prime_location_name": lot.prime_location_name if lot else None,
            "parking_timestamp": res.parking_timestamp if res.parking_timestamp else None,
            "leaving_timestamp": res.leaving_timestamp if res.leaving_timestamp else None,
            "duration": duration_str,
            "parking_cost": res.parking_cost
        })

    return jsonify(result), 200
# ------------------------------------------------------------
# Admin Analytics
# ------------------------------------------------------------
@admin_bp.route("/analytics", methods=["GET"])
@jwt_required()
@cache.cached(timeout=300)
def admin_analytics():
    check = check_admin()
    if check:
        return check

    # Join Reservation → ParkingSpot → ParkingLot
    analytics = (
        db.session.query(
            ParkingLot.prime_location_name.label("lot_name"),
            func.count(Reservation.id).label("total_reservations"),
            func.coalesce(func.sum(Reservation.parking_cost), 0).label("total_revenue"),
        )
        .join(ParkingSpot, ParkingSpot.id == Reservation.spot_id)
        .join(ParkingLot, ParkingLot.id == ParkingSpot.lot_id)
        .group_by(ParkingLot.id)
        .all()
    )

    # Convert query results to list of dicts
    data = [
        {
            "lot_name": a.lot_name,
            "total_reservations": int(a.total_reservations),
            "total_revenue": float(a.total_revenue),
        }
        for a in analytics
    ]

    return jsonify(data), 200
