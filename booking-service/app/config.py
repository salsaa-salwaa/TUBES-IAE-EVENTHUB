import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bookings.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'dev-secret-123')
    TICKET_SERVICE_URL: str = os.getenv('TICKET_SERVICE_URL', 'http://localhost:4002/graphql')
    EVENT_SERVICE_URL: str = os.getenv("EVENT_SERVICE_URL", "http://localhost:4001/graphql")

settings = Settings()
