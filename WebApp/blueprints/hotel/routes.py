from WebApp.blueprints.hotel import bp
from WebApp.blueprints.hotel.schema import HotelsListSchema, HotelsRequestSchema, HotelsResponseSchema
from WebApp.blueprints.hotel.service import HotelsService
from apiflask import HTTPError
from WebApp.extensions import auth
from WebApp.blueprints import role_required

@bp.route('/')
def index():
    return "This is the Hotels Blueprint"

@bp.get('/list')
@bp.output(HotelsListSchema(many=True))
def hotels_list_all():
    success, hotels = HotelsService.hotels_list_all()
    if success:
        return hotels, 200
    raise HTTPError(message=hotels, status_code=400)

@bp.get('/<int:hid>')
@bp.output(HotelsResponseSchema)
def hotel_get(hid):
    success, hotel = HotelsService.hotel_get(hid)
    if success:
        return hotel, 200
    raise HTTPError(message=hotel, status_code=404)

@bp.post('/add')
@bp.input(HotelsRequestSchema, location="json")
@bp.output(HotelsResponseSchema)
@bp.auth_required(auth)
@role_required(["Administrator"])
def hotel_add(json_data):
    success, hotel = HotelsService.hotel_create(json_data)
    if success:
        return hotel, 201
    raise HTTPError(message=hotel, status_code=400)