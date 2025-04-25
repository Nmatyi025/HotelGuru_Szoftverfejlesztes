from WebApp.blueprints.room import bp
from WebApp.blueprints.room.schema import RoomsListSchema, RoomsRequestSchema, RoomsResponseSchema
from WebApp.blueprints.room.service import RoomsService
from apiflask import HTTPError

@bp.route('/')
def index():
    """Index route for the Rooms Blueprint."""
    return 'This is The Rooms Blueprint'

@bp.get('/list')
@bp.output(RoomsListSchema(many=True))
def rooms_list_all():
    """
    List all available rooms.
    """
    success, response = RoomsService.rooms_list_all()
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)

@bp.delete('/delete/<int:rid>')
def room_delete(rid):
    """
    Delete a room by ID.
    """
    success, response = RoomsService.room_delete(rid)
    if success:
        return {"message": response}, 200
    raise HTTPError(message=response, status_code=400)

@bp.post('/add')
@bp.input(RoomsRequestSchema, location="json")
@bp.output(RoomsResponseSchema)
def room_add_new(json_data):
    """
    Add a new room.
    """
    success, response = RoomsService.room_add(json_data)
    if success:
        return response, 200  # Changed from 201 to 200
    raise HTTPError(message=response, status_code=400)

@bp.put('/update/<int:rid>')
@bp.input(RoomsRequestSchema, location="json")
@bp.output(RoomsResponseSchema)
def room_update(rid, json_data):
    """
    Update a room by its ID.
    """
    success, response = RoomsService.room_update(rid, json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)

@bp.get('/hotel/<int:hotel_id>')
@bp.output(RoomsListSchema(many=True))
def room_list_by_hotel(hotel_id):
    """
    List rooms by hotel ID.
    """
    success, result = RoomsService.room_list_by_hotel(hotel_id)
    if success:
        return result, 200
    raise HTTPError(message=result, status_code=400)

@bp.get('/<int:rid>')
@bp.output(RoomsResponseSchema)
def room_get_by_id(rid):
    """
    Get a room by its ID.
    """
    success, result = RoomsService.room_get_by_id(rid)
    if success:
        return result, 200
    raise HTTPError(message=result, status_code=404)