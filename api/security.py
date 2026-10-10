from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import get_required_env, load_security_config

_cfg = load_security_config()
SECRET_KEY = get_required_env("JWT_SECRET_KEY")


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=_cfg.token_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=_cfg.jwt_algorithm)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[_cfg.jwt_algorithm])
    return payload["sub"]
