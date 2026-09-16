"""User authentication and registration router (Constitution Article IV & V)."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.repositories import usuarios as usuarios_repo
from app.schemas.usuario import UsuarioCreate, UsuarioOut, Token

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar_usuario(
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db),
) -> UsuarioOut:
    """Register a new user with hashed password (Constitution Article IV.1)."""
    existente = usuarios_repo.obtener_por_email(db, email=usuario_in.email)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )
    hashed_password = get_password_hash(usuario_in.password)
    usuario = usuarios_repo.guardar(db, email=usuario_in.email, hashed_password=hashed_password)
    return usuario


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
def login_para_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """OAuth2 password flow token issuance (Constitution Article IV.2)."""
    usuario = usuarios_repo.obtener_por_email(db, email=form_data.username)
    if not usuario or not verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": usuario.email})
    return Token(access_token=access_token, token_type="bearer")
