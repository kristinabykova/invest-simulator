import jwt
import bcrypt

from core.config import Settings


def encode_jwt(
    payload: dict, key: str = Settings.SECRET_KEY, algorithm: str = Settings.ALGORITHM
):
    encoded = jwt.encode(payload, key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    key: str = Settings.SECRET_KEY,
    algorithm: str = Settings.ALGORITHM,
):
    decoded = jwt.decode(token, key, algorithms=algorithm)
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)
