import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "secret-key-tubes")

def get_current_user(info):
    request = info.context["request"]
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise Exception("Authorization header missing")

    token = auth_header.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


def require_admin(info):
    user = get_current_user(info)

    if user.get("role") != "ADMIN":
        raise Exception("Admin access required")

    return user
