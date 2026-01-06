from jose import jwt, JWTError
from app.config import settings

def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id, payload
    except JWTError as e:
        print(f"DEBUG: JWT Decode Error: {e}")
        return None
