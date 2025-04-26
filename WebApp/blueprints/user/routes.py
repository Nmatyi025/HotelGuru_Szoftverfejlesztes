from WebApp.extensions import auth
from WebApp.blueprints import role_required
from WebApp.blueprints.user import bp
from WebApp.blueprints.user.schemas import UserResponseSchema, UserRequestSchema, UserLoginSchema, RoleSchema
from WebApp.blueprints.user.service import UserService
from apiflask import HTTPError
from apiflask.fields import String, Email, Nested, Integer, List

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

bp.get('/roles')
@bp.auth_required(auth) 
@bp.doc(tags=["user"])
@bp.output(RoleSchema(many=True))
@role_required(["Administrator"])
def user_list_roles():
    success, response = UserService.user_list_roles()
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)

@bp.get('/myroles')
@bp.doc(tags=["user"])
@bp.output(RoleSchema(many=True))
@bp.auth_required(auth)
@role_required(["Administrator"])
def user_list_user_roles():
    success, response = UserService.list_user_roles(auth.current_user.get("user_id"))
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.get('/roles/<int:uid>')
@bp.doc(tags=["user"])
@bp.output(RoleSchema(many=True))
def user_list_user_roles_old(uid):
    success, response = UserService.list_user_roles(uid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)