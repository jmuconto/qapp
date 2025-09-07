# app/auth.py
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models import User
from tortoise.exceptions import DoesNotExist
from app.config import config  # optional, you can load JWT secret here

# -----------------------
# Password hashing setup
# -----------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

# -----------------------
# JWT token setup
# -----------------------
JWT_SECRET = config.get("jwt_secret", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def create_access_token(user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT token"""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    return token

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from JWT token"""
    from tortoise.exceptions import DoesNotExist
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = await User.get(id=user_id)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except (jwt.InvalidTokenError, DoesNotExist):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# -----------------------
# User authentication
# -----------------------
async def authenticate_user(phone: str, password: str) -> User:
    """Authenticate a user by phone and password"""
    try:
        user = await User.get(phone=phone)
    except DoesNotExist:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

# -----------------------
# Example login endpoint (to be included in users.py router)
# -----------------------
"""
from fastapi import APIRouter, Form
from app.auth import authenticate_user, create_access_token

router = APIRouter()

@router.post("/login")
async def login(phone: str = Form(...), password: str = Form(...)):
    user = await authenticate_user(phone, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    token = create_access_token(user_id=user.id, role=user.role)
    return {"access_token": token, "token_type": "bearer", "role": user.role}
"""
