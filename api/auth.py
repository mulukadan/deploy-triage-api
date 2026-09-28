import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext


SECRET_KEY = os.getenv("JWT_SECRET", "dev-only-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Demo user for the capstone.
# In production, use a real database and hashed credentials.
DEMO_USERS = {
    "mercy": {
        "username": "mercy",
        "hashed_password": pwd_context.hash("afyaplus123"),
        "role": "dispatcher",
    }
}


def authenticate_user(username: str, password: str):
    user = DEMO_USERS.get(username)

    if not user:
        return None

    if not pwd_context.verify(password, user["hashed_password"]):
        return None

    return user


def create_access_token(data: dict):
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload["exp"] = expire

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")

        if not username:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = DEMO_USERS.get(username)

    if not user:
        raise credentials_exception

    return user


def require_dispatcher(
    current_user=Depends(get_current_user),
):
    if current_user.get("role") != "dispatcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispatcher role required",
        )

    return current_user
