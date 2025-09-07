# app/routers/users.py
from fastapi import APIRouter, Form, Depends, HTTPException
from typing import List
from app.models import User
from app.schemas import UserRead, UserCreate
from app.auth import hash_password, authenticate_user, create_access_token, get_current_user

router = APIRouter()


# -----------------------
# Register a new user
# -----------------------
@router.post("/register", response_model=UserRead)
async def register_user(
    name: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    current_user: User = Depends(get_current_user)  # Optional: Only admin can create users
):
    """
    Register a new user. Only admin can create users.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create users")

    existing_user = await User.get_or_none(phone=phone)
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone already registered")

    user = await User.create(
        name=name,
        phone=phone,
        password_hash=hash_password(password),
        role=role
    )
    return UserRead.from_orm(user)


# -----------------------
# Login user
# -----------------------
@router.post("/login")
async def login_user(phone: str = Form(...), password: str = Form(...)):
    """
    Login user and return JWT token
    """
    user = await authenticate_user(phone, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    token = create_access_token(user_id=user.id, role=user.role)
    return {"access_token": token, "token_type": "bearer", "role": user.role}


# -----------------------
# List all users (admin only)
# -----------------------
@router.get("/", response_model=List[UserRead])
async def list_users(current_user: User = Depends(get_current_user)):
    """
    List all registered users. Admin only.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    users = await User.all()
    return [UserRead.from_orm(u) for u in users]


# -----------------------
# Get current user info
# -----------------------
@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get info about the currently logged-in user
    """
    return UserRead.from_orm(current_user)
