from WebApp.blueprints.room.schema import RoomsResponseSchema, RoomsListSchema
from WebApp import db
from WebApp.models.room import Room
from sqlalchemy import select

class RoomsService:

    @staticmethod
    def rooms_list_all():
        """
        List all available rooms.
        """
        rooms = db.session.execute(select(Room)).scalars()
        return True, rooms

    @staticmethod
    def room_delete(rid):
        """
        Delete a room by ID.
        """
        try:
            room = db.session.get(Room, rid)
            if room:
                db.session.delete(room)
                db.session.commit()
                return True, "Room deleted successfully."
            return False, "Room not found."
        except Exception as ex:
            return False, f"room_delete() error: {str(ex)}"

    @staticmethod
    def room_add(request):
        """
        Add a new room.
        """
        try:
            # Create and add the room
            room = Room(
                room_number=request.get("room_number"),
                hotel_id=request.get("hotel_id"),
                price_per_night=request.get("price_per_night"),
                available=request.get("available", True),
                description=request.get("description"),
                photo_urls=request.get("photo_urls")
            )
            db.session.add(room)
            db.session.commit()
            
            # Return the dictionary representation of the room
            # This allows apiflask to properly serialize the response
            room_schema = RoomsResponseSchema()
            return True, room
        except Exception as ex:
            return False, f"room_add() error: {str(ex)}"

    @staticmethod
    def room_update(rid, request):
        """
        Update a room by its ID.
        """
        try:
            # Fetch the room and update its fields
            room = db.session.get(Room, rid)
            if room:
                if "room_number" in request:
                    room.room_number = request["room_number"]
                if "hotel_id" in request:
                    room.hotel_id = request["hotel_id"]
                if "price_per_night" in request:
                    room.price_per_night = request["price_per_night"]
                if "available" in request:
                    room.available = request["available"]
                if "description" in request:
                    room.description = request["description"]
                if "photo_urls" in request:
                    room.photo_urls = request["photo_urls"]
                
                db.session.commit()
                return True, room
            return False, "Room not found."
        except Exception as ex:
            return False, f"room_update() error: {str(ex)}"

    @staticmethod
    def room_list_by_hotel(hotel_id):
        """
        List rooms by hotel ID.
        """
        try:
            rooms = db.session.execute(
                select(Room).filter(Room.hotel_id == hotel_id)
            ).scalars().all()
            return True, rooms
        except Exception as ex:
            return False, f"room_list_by_hotel() error: {str(ex)}"

    @staticmethod
    def room_get_by_id(rid):
        """
        Get a room by its ID.
        """
        try:
            room = db.session.get(Room, rid)
            if not room:
                return False, "Room not found."
            return True, room
        except Exception as ex:
            return False, f"room_get_by_id() error: {str(ex)}"