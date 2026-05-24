from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import create_token, current_user, hash_secret, user_response, verify_secret
from ..database import get_db
from ..models import User
from ..schemas import AuthRequest


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(request: AuthRequest, db: Session = Depends(get_db)) -> dict:
    username = request.username.strip()
    if len(username) < 3 or len(request.secret) < 6:
        raise HTTPException(status_code=400, detail="用户名至少 3 位，密钥至少 6 位")
    if db.scalar(select(User).where(User.username == username)):
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=username, secret_hash=hash_secret(request.secret))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_token(user), "user": user_response(user)}


@router.post("/login")
def login(request: AuthRequest, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.username == request.username.strip()))
    if user is None or not verify_secret(request.secret, user.secret_hash):
        raise HTTPException(status_code=401, detail="用户名或密钥错误")
    return {"token": create_token(user), "user": user_response(user)}


@router.get("/me")
def me(user: User = Depends(current_user)) -> dict:
    return user_response(user)
