from WebApp.blueprints.reservation import bp
from WebApp.blueprints.reservation.schema import ReservationRequestSchema, ReservationResponseSchema
from WebApp.blueprints.reservation.service import ReservationService
from apiflask import HTTPError

@bp.route('/')
def index():
    """Index route for the Reservation Blueprint."""
    return 'This is The Reservation Blueprint'

@bp.post('/add')
@bp.input(ReservationRequestSchema, location="json")
@bp.output(ReservationResponseSchema)
def add_reservation(json_data):
    """Add a new reservation."""
    success, response = ReservationService.add_reservation(json_data)
    if success:
        return response, 201
    raise HTTPError(400, message=response)

@bp.get('/<int:rid>')
@bp.output(ReservationResponseSchema)
def get_reservation(rid):
    """Get a reservation by its ID."""
    success, response = ReservationService.get_reservation(rid)
    if success:
        return response, 200
    raise HTTPError(404, message=response)

@bp.delete('/delete/<int:rid>')
def delete_reservation(rid):
    """Delete a reservation by its ID."""
    success, response = ReservationService.delete_reservation(rid)
    if success:
        return {"message": response}, 200
    raise HTTPError(400, message=response)