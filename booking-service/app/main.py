from fastapi import FastAPI, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, Base, get_db
from app.schema.schema import schema
from app.auth import get_user_from_token
from contextlib import asynccontextmanager
from app.graphiql_modern import MODERN_GRAPHIQL_HTML

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

from fastapi.responses import HTMLResponse

@app.get("/graphql", response_class=HTMLResponse)
async def get_graphiql():
    return MODERN_GRAPHIQL_HTML

@app.post("/graphql")
async def graphql_handler(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        data = {}
        
    query = data.get("query")
    variables = data.get("variables")
    
    if not query:
        return {"errors": [{"message": "No query provided"}]}

    auth_header = request.headers.get("Authorization")
    user_id = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user_data = get_user_from_token(token)
        if user_data:
            user_id = user_data[0]
            
    context = {
        "db": db,
        "user_id": user_id,
        "request": request,
    }
    
    result = await schema.execute_async(
        query,
        variable_values=variables,
        context_value=context,
    )
    
    response = {}
    if result.errors:
        response["errors"] = [{"message": str(e)} for e in result.errors]
    if result.data:
        response["data"] = result.data
        
    return response

@app.get("/")
def read_root():
    return {"message": "Booking Service is running"}
