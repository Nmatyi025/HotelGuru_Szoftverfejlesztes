from WebApp.blueprints.room.schema import RoomsResponseSchema, RoomsListSchema
from WebApp import db
from WebApp.models.room import Room
from sqlalchemy import select

class HotelsService:
    """
    Service class for hotel-related operations.
    """

    @staticmethod
    def hotels_list_all():
        """
        List all available hotels.
        """
        hotels = db.session.execute(select(Room)).scalars()
        return True, hotels

    @staticmethod
    def hotel_delete(hid):
        """
        Delete a hotel by ID.
        """
        try:
            hotel = db.session.get(Room, hid)
            if hotel:
                db.session.delete(hotel)
                db.session.commit()
                return True, "Hotel deleted successfully."
            return False, "Hotel not found."
        except Exception as ex:
            return False, f"hotel_delete() error: {str(ex)}"

    @staticmethod
    def hotel_get(hid):
        """
        Get details of a specific hotel by ID.
        """
        try:
            hotel = db.session.get(Room, hid)
            if hotel:
                return True, hotel
            return False, "Hotel not found."
        except Exception as ex:
            return False, f"hotel_get() error: {str(ex)}"

    @staticmethod
    def hotel_create(data):
        """
        Create a new hotel.
        """
        try:
            new_hotel = Room(**data)
            db.session.add(new_hotel)
            db.session.commit()
            return True, new_hotel
        except Exception as ex:
            return False, f"hotel_create() error: {str(ex)}"

    @staticmethod
    def hotel_update(hid, data):
        """
        Update an existing hotel by ID.
        """
        try:
            hotel = db.session.get(Room, hid)
            if hotel:
                for key, value in data.items():
                    setattr(hotel, key, value)
                db.session.commit()
                return True, hotel
            return False, "Hotel not found."
        except Exception as ex:
            return False, f"hotel_update() error: {str(ex)}"

    @staticmethod
    def hotel_list_all():
        """
        List all hotels.
        """
        try:
            hotels = db.session.execute(select(Room)).scalars()
            return True, hotels
        except Exception as ex:
            return False, f"hotel_list_all() error: {str(ex)}"

    @staticmethod
    def hotel_list_by_id(hid):
        """
        List a hotel by ID.
        """
        try:
            hotel = db.session.get(Room, hid)
            if hotel:
                return True, hotel
            return False, "Hotel not found."
        except Exception as ex:
            return False, f"hotel_list_by_id() error: {str(ex)}"

    @staticmethod
    def hotel_list_by_name(name):
        """
        List hotels by name.
        """
        try:
            hotels = db.session.execute(select(Room).filter(Room.hotel_name == name)).scalars()
            return True, hotels
        except Exception as ex:
            return False, f"hotel_list_by_name() error: {str(ex)}"

    @staticmethod
    def hotel_list_by_location(location):
        """
        List hotels by location.
        """
        try:
            hotels = db.session.execute(select(Room).filter(Room.location == location)).scalars()
            return True, hotels
        except Exception as ex:
            return False, f"hotel_list_by_location() error: {str(ex)}"

    @staticmethod
    def hotel_list_by_rating(rating):
        """
        List hotels by rating.
        """
        try:
            hotels = db.session.execute(select(Room).filter(Room.rating == rating)).scalars()
            return True, hotels
        except Exception as ex:
            return False, f"hotel_list_by_rating() error: {str(ex)}"



