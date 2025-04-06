from apiflask import APIBlueprint
from app.blueprints.user import bp as bp_user
bp = APIBlueprint('main', __name__, tag="Main")

bp.register_blueprint(bp_user, url_prefix='/user')

