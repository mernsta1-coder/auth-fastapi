# app/middleware/auth_middleware.py
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
import os

# SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

async def jwt_middleware(request: Request, call_next):
    # Skip login/register and Swagger docs
    if request.url.path.startswith("/auth/login") or request.url.path.startswith("/auth/register"):
        return await call_next(request)
    
    if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json") or request.url.path.startswith("/redoc"):
        return await call_next(request)

    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid token"})
    
    token = auth_header.split(" ")[1]

    try:   
        PUBLIC_KEY = os.getenv("PUBLIC_KEY").replace("\\n", "\n")
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        print("payload",payload)
        request.state.user = payload  # Save payload to request.state
    except JWTError:
        return JSONResponse(status_code=401, content={"detail": "Invalid token"})
    
    response = await call_next(request)
    return response