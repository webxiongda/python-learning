from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import User


TOKEN_SECRET = os.environ.get("PYTHON_WORKBENCH_SECRET", "local-python-workbench-secret")

# 免登录模式：开启后未携带 token 的请求自动落到该默认用户，而不是抛 401。
# 业务数据全部按 user_id 隔离，所以必须落到真实用户行，不能只放行权限。
AUTO_LOGIN_USERNAME = os.environ.get("PYTHON_WORKBENCH_AUTO_USER", "").strip()
AUTO_LOGIN_SECRET = os.environ.get("PYTHON_WORKBENCH_AUTO_SECRET", "auto-login-placeholder-secret")


def hash_secret(secret: str, salt: Optional[str] = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"{salt}${base64.urlsafe_b64encode(digest).decode('ascii')}"


def verify_secret(secret: str, stored: str) -> bool:
    salt, expected = stored.split("$", 1)
    return hmac.compare_digest(hash_secret(secret, salt).split("$", 1)[1], expected)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "username": user.username,
        "exp": (datetime.utcnow() + timedelta(days=30)).isoformat(),
    }
    body = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(TOKEN_SECRET.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest()
    return f"{body}.{_b64(signature)}"


def parse_token(token: str) -> dict:
    try:
        body, signature = token.split(".", 1)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效登录凭证") from error
    expected = _b64(hmac.new(TOKEN_SECRET.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效登录凭证")
    payload = json.loads(_unb64(body))
    if datetime.fromisoformat(payload["exp"]) < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已过期")
    return payload


def default_user(db: Session) -> User:
    """获取（或创建）免登录模式使用的默认用户。

    业务表全部按 user_id 外键关联，因此必须落到一条真实用户记录，
    否则即使放行鉴权，下游按 user_id 查询也会拿不到数据。
    """
    username = AUTO_LOGIN_USERNAME or "auto_user"
    user = db.scalar(select(User).where(User.username == username))
    if user is not None:
        return user
    user = User(username=username, secret_hash=hash_secret(AUTO_LOGIN_SECRET))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auto_login_enabled() -> bool:
    """默认开启免登录；设置 PYTHON_WORKBENCH_AUTO_USER=off 可关回原登录流程。"""
    return AUTO_LOGIN_USERNAME.lower() != "off"


def current_user(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        if auto_login_enabled():
            return default_user(db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    try:
        payload = parse_token(authorization.removeprefix("Bearer ").strip())
    except HTTPException:
        if auto_login_enabled():
            return default_user(db)
        raise
    user = db.scalar(select(User).where(User.id == int(payload["sub"])))
    if user is None:
        if auto_login_enabled():
            return default_user(db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


def user_response(user: User) -> dict:
    return {"id": user.id, "username": user.username}
