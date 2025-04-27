from WebApp.blueprints.room import bp
from WebApp.blueprints.room.schema import RoomsListSchema, RoomsRequestSchema, RoomsResponseSchema
from WebApp.blueprints.room.service import RoomsService
from apiflask import HTTPError
from WebApp.extensions import auth
from WebApp.blueprints import role_required

@bp.get("/hotels")
@bp.doc("list_hotels")
@bp.response(200, RoomsListSchema(many=True))
@bp.auth("jwt")
@bp.role_required("admin", "user")
def hotels_list_all():
    """
    List all available hotels.
    """
    success, hotels = HotelsService.hotels_list_all()
    if not success:
        raise HTTPError(500, "Error fetching hotels.")
    return RoomsListSchema(many=True).dump(hotels), 200


@bp.get("/hotels/<int:hid>")
@bp.doc("get_hotel")
@bp.response(200, HotelsResponseSchema)
@bp.auth("jwt")
@bp.role_required("admin", "user")
def hotel_get(hid):
    """
    Get details of a specific hotel by ID.
    """
    success, hotel = HotelsService.hotel_get(hid)
    if not success:
        raise HTTPError(404, "Hotel not found.")
    return HotelsResponseSchema().dump(hotel), 200

@bp.post("/hotels")
@bp.doc("create_hotel")
@bp.input(HotelsRequestSchema)
@bp.response(201, RoomsResponseSchema)
@bp.auth("jwt")
@bp.role_required("admin")
def hotel_create(data):
    """
    Create a new hotel.
    """
    success, hotel = HotelsService.hotel_create(data)
    if not success:
        raise HTTPError(400, "Error creating hotel.")
    return RoomsResponseSchema().dump(hotel), 201