from WebApp import app, db
from flask import jsonify
from WebApp.hotelmanager import HotelManager
from WebApp.models import Hotel, Room

hm = HotelManager(db)

@app.get("/api/hotels")
def get_hotels():
    hotel_list = list(map(lambda hotel: hotel.to_dict(), hm.hotels))
    return jsonify(hotel_list)

@app.get("/api/rooms")
def get_rooms():
    room_list = list(map(lambda room: room.to_dict(), hm.rooms))
    return jsonify(room_list)

@app.get("/api/hotel/<id>")
def get_hotel(id: int):
    hotel = hm.get_hotel(id)
    if hotel:
        return jsonify(hotel.to_dict())
    return jsonify({"error": "Hotel not found"}), 404

@app.get("/api/room/<id>")
def get_room(id: int):
    room = hm._db.session.query(Room).get(id)
    if room:
        return jsonify(room.to_dict())
    return jsonify({"error": "Room not found"}), 404
