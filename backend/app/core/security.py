import base64
import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.admin_user import AdminUser, AdminUserCRUD

PASSWORD_SALT_BYTES = 16
PASSWORD_KEY_BYTES = 64
PASSWORD_SCRYPT_N = 2**14
PASSWORD_SCRYPT_R = 8
PASSWORD_SCRYPT_P = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """Создаёт устойчивый к перебору хеш пароля с солью."""
    salt = os.urandom(PASSWORD_SALT_BYTES)
    digest = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=PASSWORD_SCRYPT_N,
        r=PASSWORD_SCRYPT_R,
        p=PASSWORD_SCRYPT_P,
        dklen=PASSWORD_KEY_BYTES,
    )
    encoded_salt = base64.urlsafe_b64encode(salt).decode()
    encoded_digest = base64.urlsafe_b64encode(digest).decode()
    return f"scrypt${encoded_salt}${encoded_digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Проверяет пароль без раскрытия информации о сохранённом хеше."""
    try:
        algorithm, salt_value, digest_value = stored_hash.split("$", 2)
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_value.encode())
        expected = base64.urlsafe_b64decode(digest_value.encode())
        actual = hashlib.scrypt(
            password.encode(),
            salt=salt,
            n=PASSWORD_SCRYPT_N,
            r=PASSWORD_SCRYPT_R,
            p=PASSWORD_SCRYPT_P,
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(admin_id: int) -> str:
    """Создаёт JWT с идентификатором администратора и сроком действия."""
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(admin_id), "exp": expires_at},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    """Возвращает активного администратора из Bearer JWT."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        admin_id = int(subject)
    except (JWTError, TypeError, ValueError) as exc:
        raise credentials_error from exc

    admin = AdminUserCRUD.get(db, admin_id)
    if admin is None or not admin.is_active:
        raise credentials_error
    return admin
