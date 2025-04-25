from WebApp import db
from WebApp.models.booking import Booking as Reservation
from WebApp.blueprints.reservation.schema import ReservationResponseSchema
from sqlalchemy import select

class ReservationService:

    @staticmethod
    def add_reservation(request):
        """Add a new reservation."""
        try:
            # Create reservation with the correct field names from the model
            reservation = Reservation(
                user_id=request.get("user_id"),
                room_id=request.get("room_id"),
                start_date=request.get("start_date"),
                end_date=request.get("end_date"),
                status=request.get("status", "pending")
            )
            db.session.add(reservation)
            db.session.commit()
            
            # Create a dictionary with the fields to avoid serialization issues
            result = {
                'id': reservation.id,
                'user_id': reservation.user_id,
                'room_id': reservation.room_id,
                'start_date': reservation.start_date,
                'end_date': reservation.end_date,
                'status': reservation.status,
                'created_on': reservation.created_on
            }
            
            return True, result
        except Exception as ex:
            return False, f"add_reservation() error: {str(ex)}"

    @staticmethod
    def get_reservation(rid):
        """Get a reservation by its ID."""
        try:
            reservation = db.session.get(Reservation, rid)
            if not reservation:
                return False, "Reservation not found."
                
            # Create a dictionary with the fields to avoid serialization issues
            result = {
                'id': reservation.id,
                'user_id': reservation.user_id,
                'room_id': reservation.room_id,
                'start_date': reservation.start_date,
                'end_date': reservation.end_date,
                'status': reservation.status,
                'created_on': reservation.created_on
            }
            
            return True, result
        except Exception as ex:
            return False, f"get_reservation() error: {str(ex)}"

    @staticmethod
    def delete_reservation(rid):
        """Delete a reservation by its ID."""
        try:
            reservation = db.session.get(Reservation, rid)
            if reservation:
                db.session.delete(reservation)
                db.session.commit()
                return True, "Reservation deleted successfully."
            return False, "Reservation not found."
        except Exception as ex:
            return False, f"delete_reservation() error: {str(ex)}"