import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import User as UserModel, db
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, verify_jwt_in_request, get_jwt
import bcrypt
from functools import wraps
from flask import request
import re

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
PHONE_REGEX = r'^\+?[0-9]{10,15}$'

def validate_email(email):
    if not re.match(EMAIL_REGEX, email):
        raise Exception("Invalid email format")

def validate_phone(phone):
    if phone and not re.match(PHONE_REGEX, phone):
        raise Exception("Invalid phone number format (must be 10-15 digits)")

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "ADMIN":
            raise Exception("Access Denied: Admin role required")
        return fn(*args, **kwargs)
    return wrapper

def owner_or_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        
        if claims.get("role") == "ADMIN":
            return fn(*args, **kwargs)
            
        target_id = kwargs.get('id')
        if str(target_id) == str(current_user_id):
            return fn(*args, **kwargs)
            
        raise Exception("Access Denied: You can only modify your own account")
    return wrapper

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        exclude_fields = ('password',)

class AuthPayload(graphene.ObjectType):
    access_token = graphene.String()
    user = graphene.Field(UserType)

class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        phone_number = graphene.String()
        address = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, name, email, password, **kwargs):
        validate_email(email)
        if 'phone_number' in kwargs:
            validate_phone(kwargs['phone_number'])

        if UserModel.query.filter_by(email=email).first():
            raise Exception("Email already registered")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = UserModel(
            name=name,
            email=email,
            password=hashed_password,
            phone_number=kwargs.get('phone_number'),
            address=kwargs.get('address')
        )
        
        db.session.add(user)
        db.session.commit()
        return CreateUser(user=user)

class Login(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    Output = AuthPayload

    def mutate(self, info, email, password):
        user = UserModel.query.filter_by(email=email).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            raise Exception("Invalid credentials")

        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        return AuthPayload(access_token=access_token, user=user)

class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        phone_number = graphene.String()
        address = graphene.String()

    user = graphene.Field(UserType)

    @owner_or_admin_required
    def mutate(self, info, id, **kwargs):
        user = UserModel.query.get(id)
        if not user:
            raise Exception("User not found")
        
        if 'phone_number' in kwargs:
             validate_phone(kwargs['phone_number'])

        if 'name' in kwargs: user.name = kwargs['name']
        if 'phone_number' in kwargs: user.phone_number = kwargs['phone_number']
        if 'address' in kwargs: user.address = kwargs['address']
        
        db.session.commit()
        return UpdateUser(user=user)

class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    ok = graphene.Boolean()

    @admin_required
    def mutate(self, info, id):
        user = UserModel.query.get(id)
        if not user:
            raise Exception("User not found")
        db.session.delete(user)
        db.session.commit()
        return DeleteUser(ok=True)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login = Login.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    me = graphene.Field(UserType, token=graphene.String(required=True))

    def resolve_users(self, info):
        return UserModel.query.all()

    user = graphene.Field(UserType, id=graphene.ID(required=True))

    ticket_service_token = graphene.String()

    def resolve_user(self, info, id):
        auth_header = info.context.headers.get('Authorization')
        if not auth_header:
             raise Exception("Missing Authorization Header")
        
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "ADMIN":
                 raise Exception("Access Denied: Admin role required to view other user details")
        except Exception as e:
            raise Exception(f"Auth Error: {str(e)}")

        return UserModel.query.get(id)

    def resolve_me(self, info, token):
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
            return UserModel.query.get(user_id)
        except Exception as e:
            raise Exception(f"Invalid Token: {str(e)}")

schema = graphene.Schema(query=Query, mutation=Mutation)
