# app/middleware.py
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
import jwt
from typing import Optional
from app.config import config  # Assuming you have config.py

logger = logging.getLogger("qapp_middleware")
logger.setLevel(logging.INFO)

# -----------------------
# CORS Middleware Setup
# -----------------------
def add_cors_middleware(app):
    """
    Add CORS middleware to allow requests from frontend origins.
    """
    origins = config.get("cors_origins", ["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS middleware added with origins: {origins}")


# -----------------------
# Request Logging Middleware
# -----------------------
async def log_requests(request: Request, call_next):
    """
    Logs incoming HTTP requests and response times.
    """
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - status: {response.status_code} - time: {process_time:.3f}s")
    return response


# -----------------------
# Simple JWT Authentication Middleware
# -----------------------
async def jwt_auth_middleware(request: Request, call_next):
    """
    Optional JWT authentication for protected routes.
    Add 'Authorization: Bearer <token>' header.
    """
    if request.url.path.startswith("/users") or request.url.path.startswith("/admin"):
        auth_header: Optional[str] = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Missing Authorization header"}, status_code=401)
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, config.get("jwt_secret", "secret"), algorithms=["HS256"])
            request.state.user = payload  # Make user info available in endpoints
        except jwt.ExpiredSignatureError:
            return JSONResponse({"detail": "Token expired"}, status_code=401)
        except jwt.InvalidTokenError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)
    return await call_next(request)


# -----------------------
# Exception Logging Middleware
# -----------------------
async def exception_logging_middleware(request: Request, call_next):
    """
    Logs any unhandled exceptions in requests.
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception for {request.url.path}: {e}")
        return JSONResponse({"detail": "Internal Server Error"}, status_code=500)
