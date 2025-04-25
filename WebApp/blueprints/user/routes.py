from WebApp.blueprints.user import bp
from WebApp.blueprints.user.schemas import UserRequestSchema, UserResponseSchema, UserLoginSchema
from WebApp.blueprints.user.service import UserService
from apiflask import HTTPError

@bp.route("/")
def index():
    return "Welcome to the user API!"

@bp.post('/registrate')
@bp.input(UserRequestSchema, location="json")
@bp.output(UserResponseSchema)
def user_registrate(json_data):
    success, response = UserService.user_registrate(json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)

@bp.post('/login')
@bp.doc(tags=["user"])
@bp.input(UserLoginSchema, location="json")
@bp.output(UserResponseSchema)
def user_login(json_data):
    success, response = UserService.user_login(json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)