
from flask import Flask
from models.db_setup import init_db, db
from models import User, ParkingLot, ParkingSpot, Reservation

app = Flask(__name__)
init_db(app)

@app.route("/")
def home():
    return {"message": "Vehicle Parking App Backend Running!"}

if __name__ == "__main__":
    app.run(debug=True)
