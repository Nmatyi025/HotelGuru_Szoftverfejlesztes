from WebApp.blueprints.hotel.schema import HotelsResponseSchema, HotelsListSchema
from WebApp import db
from WebApp.models.hotel import Hotel
from sqlalchemy import select

class HotelsService:
    @staticmethod
    def hotels_list_all():
        hotels = db.session.execute(select(Hotel)).scalars().all()
        return True, HotelsListSchema(many=True).dump(hotels)

    @staticmethod
    def hotel_get(hid):
        hotel = db.session.get(Hotel, hid)
        if hotel:
            return True, HotelsResponseSchema().dump(hotel)
        return False, "Hotel not found."

    @staticmethod
    def hotel_create(data):
        try:
            hotel = Hotel(**data)
            db.session.add(hotel)
            db.session.commit()
            return True, HotelsResponseSchema().dump(hotel)
        except Exception as ex:
            return False, f"hotel_create() error: {str(ex)}"



