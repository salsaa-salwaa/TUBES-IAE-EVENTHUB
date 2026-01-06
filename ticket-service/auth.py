import os
import jwt
from functools import wraps

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-123")

def admin_required(fn):
    @wraps(fn)
    def wrapper(root, info, *args, **kwargs):
        auth_header = info.context.headers.get('Authorization')
        if not auth_header:
             raise Exception("Missing Authorization Header")
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
             raise Exception("Invalid Authorization Header format")
        
        token = parts[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            role = payload.get("role")
            if role != "ADMIN":
                 raise Exception("Access Denied: Admin role required")
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
            
        return fn(root, info, *args, **kwargs)
    return wrapper
