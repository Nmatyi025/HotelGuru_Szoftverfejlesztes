from WebApp import db
from WebApp.models.booking import Booking as Reservation
from sqlalchemy import select

class ReservationService:

    @staticmethod
    def add_reservation(request):
        """Add a new reservation."""
        try:
            reservation = Reservation(**request)
            db.session.add(reservation)
            db.session.commit()
            return True, reservation
        except Exception as ex:
            return False, f"add_reservation() error: {str(ex)}"

    @staticmethod
    def get_reservation(rid):
        """Get a reservation by its ID."""
        try:
            reservation = db.session.get(Reservation, rid)
            if not reservation:
                return False, "Reservation not found."
            return True, reservation
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