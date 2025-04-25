from apiflask import APIBlueprint

bp = APIBlueprint("main", __name__, tag="Main")

@bp.route("/")
def index():
    return "Welcome to the Hotel Guru API!"

from WebApp.blueprints.user import bp as user_bp
bp.register_blueprint(user_bp, url_prefix="/user")

from WebApp.blueprints.room import bp as bp_rooms
bp.register_blueprint(bp_rooms, url_prefix='/rooms')

from WebApp.blueprints.reservation import bp as bp_reservation
bp.register_blueprint(bp_reservation, url_prefix='/reservations')

from WebApp import routes
from WebApp import models
