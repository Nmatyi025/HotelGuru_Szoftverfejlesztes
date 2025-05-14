from WebApp import db
from WebApp.blueprints.user.schemas import UserResponseSchema, RoleSchema, PayloadSchema
from WebApp.models.user import User
from WebApp.models.role import Role
from datetime import datetime, timedelta
from authlib.jose import jwt
from flask import current_app

from sqlalchemy import select, text

class UserService:
    @staticmethod
    def token_generate(user: User):
        payload = PayloadSchema()
        payload.exp = int((datetime.now() + timedelta(minutes=30)).timestamp())
        payload.user_id = user.id
        payload.roles = RoleSchema().dump(obj=user.roles, many=True)
        return jwt.encode({'alg': 'RS256'}, PayloadSchema().dump(payload), current_app.config['SECRET_KEY']).decode()

    @staticmethod
    def user_registrate(request):
        try:
            result = db.session.execute(text("SELECT * FROM roles")).fetchall()
            print("Roles in database:", result)
            
            if db.session.execute(select(User).filter_by(email=request["email"])).scalar_one_or_none():
                return False, "E-mail already exist!"

            user = User(**request)
            user.set_password(user.password)
            
            try:
                user_role = db.session.execute(select(Role).filter_by(id=4)).scalar_one_or_none()
                if not user_role:
                    user_role = db.session.execute(select(Role).filter_by(name="User")).scalar_one_or_none()
                
                if not user_role:
                    print("No user role found in database!")
                    return False, "User role not found in database"
                    
                print("Found role:", user_role.id, user_role.name)
                user.roles.append(user_role)
                
            except Exception as role_error:
                print("Error with role:", str(role_error))
                return False, f"Role error: {str(role_error)}"

            db.session.add(user)
            db.session.commit()

            return True, UserResponseSchema().dump(user)

        except Exception as ex:
            print(f"User registration error: {str(ex)}")
            return False, f"Registration failed: {str(ex)}"
        
    @staticmethod
    def user_login(request):
        try:
            print("Login attempt with email:", request["email"])
            
            user = db.session.execute(select(User).filter_by(email=request["email"])).scalar_one()
            print(f"Found user with email {user.email}, id: {user.id}")
            print(f"Stored hashed password: {user.password}")
            
            print(f"Attempting to check password...")
            result = user.check_password(request["password"])
            print(f"Password check result: {result}")
            
            if not result:
                print(f"Password check failed")
                return False, "Incorrect e-mail or password!"
            
            print(f"Password check succeeded")
            user_schema = UserResponseSchema().dump(user)
            print(f"User schema created: {user_schema}")
            
            token = UserService.token_generate(user)
            print(f"Token generated: {token[:20]}...")
            
            user_schema["token"] = token
            return True, user_schema 
        except Exception as ex:
            print(f"Login error details: {str(ex)}")
            import traceback
            traceback.print_exc()
            return False, f"Login failed: {str(ex)}"
        
    @staticmethod
    def user_list_roles():
        roles = db.session.query(Role).all()
        return True, RoleSchema().dump(obj=roles, many=True)
    
    @staticmethod
    def list_user_roles(uid):
        user = db.session.get(User, uid)
        if user is None:
            return False, "User not found!"
        return True, RoleSchema().dump(obj=user.roles, many=True)

    @classmethod
    def add_role_to_user(cls, user_id, role_name):
        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found"
        
        role = db.session.query(Role).filter_by(name=role_name).first()
        if not role:
            return False, f"Role '{role_name}' not found"
        
        if role in user.roles:
            return True, f"User already has the role '{role_name}'"
        
        user.roles.append(role)
        db.session.commit()
        return True, f"Role '{role_name}' added to user"

    @classmethod
    def remove_role_from_user(cls, user_id, role_name):
        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found"
        
        role = db.session.query(Role).filter_by(name=role_name).first()
        if not role:
            return False, f"Role '{role_name}' not found"
        
        if role not in user.roles:
            return True, f"User doesn't have the role '{role_name}'"
        
        user.roles.remove(role)
        db.session.commit()
        return True, f"Role '{role_name}' removed from user"