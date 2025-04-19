from apiflask import APIBlueprint

bp = APIBlueprint('main', __name__, tag="default")

@bp.route('/')
def index():
    return 'This is The Main Blueprint'

from app.blueprints.room import bp as bp_rooms
bp.register_blueprint(bp_rooms, url_prefix='/rooms')

from app.blueprints.user import bp as bp_user
bp.register_blueprint(bp_user, url_prefix='/user')

