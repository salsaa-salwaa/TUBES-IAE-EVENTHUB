import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="EventHUB API Gateway")

# Service URLs from environment variables
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://booking-service:8000")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://event-service:8000")
TICKET_SERVICE_URL = os.getenv("TICKET_SERVICE_URL", "http://ticket-service:8000")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")

async def forward_request(url: str, request: Request) -> Response:
    async with httpx.AsyncClient() as client:
        method = request.method
        content = await request.body()
        headers = dict(request.headers)
        # Remove host header to avoid confusion
        headers.pop("host", None)
        params = request.query_params
        
        try:
            response = await client.request(
                method,
                url,
                content=content,
                headers=headers,
                params=params,
                timeout=10.0
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.RequestError as exc:
            return JSONResponse(
                status_code=502,
                content={"detail": f"Error connecting to service: {str(exc)}"}
            )

@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}

@app.api_route("/booking/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def booking_proxy(path: str, request: Request):
    url = f"{BOOKING_SERVICE_URL}/{path}"
    return await forward_request(url, request)

@app.api_route("/event/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def event_proxy(path: str, request: Request):
    url = f"{EVENT_SERVICE_URL}/{path}"
    return await forward_request(url, request)

@app.api_route("/ticket/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def ticket_proxy(path: str, request: Request):
    url = f"{TICKET_SERVICE_URL}/{path}"
    return await forward_request(url, request)

@app.api_route("/user/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def user_proxy(path: str, request: Request):
    url = f"{USER_SERVICE_URL}/{path}"
    return await forward_request(url, request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
