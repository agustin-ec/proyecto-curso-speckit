"""FastAPI route dependencies (Constitution Article IV.4 and VIII.1)."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import decode_access_token
from app.repositories import usuarios as usuarios_repo
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Validate Bearer JWT and return current authenticated Usuario (Art. IV.4 & VIII.1)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token no proporcionado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = usuarios_repo.obtener_por_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user


def get_gastos_repo():
    """Return gastos repository module for dependency injection (Constitution Article VIII.1)."""
    from app.repositories import gastos as gastos_repo

    return gastos_repo

