from WebApp import db
from WebApp.blueprints.user.schemas import UserResponseSchema
from WebApp.models.user import User
from WebApp.models.role import Role


from sqlalchemy import select

 
class UserService:
    @staticmethod
    def user_registrate(request):
        try:
            if db.session.execute(select(User).filter_by(email=request["email"])).scalar_one_or_none():
                return False, "E-mail already exist!"

            user = User(**request)
            user.set_password(user.password)
            user.roles.append(
                db.session.execute(select(Role).filter_by(name="User")).scalar_one()           
                )
            db.session.add(user)
            db.session.commit()

            return True, UserResponseSchema().dump(user)

        except KeyError as ke:
            return False, f"Missing required field: {str(ke)}"
        except ValueError as ve:
            return False, f"Invalid data format: {str(ve)}"
        except Exception as ex:
            # Log the actual exception for debugging
            print(f"User registration error: {str(ex)}")
            return False, f"Registration failed: {str(ex)}"
        
    @staticmethod
    def user_login(request):
        try:
           user = db.session.execute(select(User).filter_by(email=request["email"])).scalar_one()
           if not user.check_password(request["password"]):
            return False, "Incorrect e-mail or password!"
        except Exception as ex:
            return False, "Incorrect Login data!"
        return True, UserResponseSchema().dump(user)