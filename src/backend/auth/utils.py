import jwt

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
