from app.blueprints.room.schema import RoomsResponseSchema, RoomsListSchema
from app.extensions import db
from app.models.room import Room
from sqlalchemy import select

class RoomsService:

    @staticmethod
    def rooms_list_all():
        """
        List all rooms that are not marked as deleted.
        """
        rooms = db.session.execute(select(Room).filter(Room.deleted.is_(False))).scalars()
        return True, rooms

    @staticmethod
    def room_delete(rid):
        """
        Delete a room by marking it as deleted.
        """
        try:
            room = db.session.get(Room, rid)
            if room:
                room.deleted = True
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
            room = Room(**request)
            db.session.add(room)
            db.session.commit()
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
                room.name = str(request["name"])
                room.type = request["type"]
                room.status = request["status"]
                room.price = float(request["price"])
                db.session.commit()
                return True, room
            return False, "Room not found."
        except Exception as ex:
            return False, f"room_update() error: {str(ex)}"

    @staticmethod
    def room_list_type(type_name):
        """
        List rooms by their type.
        """
        try:
            if type_name is None:
                rooms = db.session.execute(
                    select(Room).filter(Room.deleted.is_(False))
                ).scalars().all()
            else:
                rooms = db.session.execute(
                    select(Room).filter(
                        Room.deleted.is_(False),
                        Room.type == type_name
                    )
                ).scalars().all()
            return True, rooms
        except Exception as ex:
            return False, f"room_list_type() error: {str(ex)}"

    @staticmethod
    def room_get_by_id(rid):
        """
        Get a room by its ID.
        """
        try:
            room = db.session.get(Room, rid)
            if not room or room.deleted:
                return False, "Room not found."
            return True, room
        except Exception as ex:
            return False, f"room_get_by_id() error: {str(ex)}"