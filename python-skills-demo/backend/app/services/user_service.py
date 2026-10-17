"""Business logic for user operations (sits between API and CRUD layers)."""

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, AppException
from app.core.security import verify_password, create_access_token
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserUpdate


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def get_user(db: Session, user_id: int) -> User:
    """Return a user by ID or raise ``NotFoundException``."""
    user = user_crud.get(db, obj_id=user_id)
    if not user:
        raise NotFoundException(detail=f"User {user_id} not found")
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Return a user by email or ``None``."""
    return user_crud.get_by_email(db, email=email)


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Return a paginated list of users."""
    return user_crud.get_multi(db, skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------

def create_user(db: Session, payload: UserCreate) -> User:
    """Register a new user, ensuring uniqueness on email."""
    if user_crud.get_by_email(db, email=payload.email):
        raise AppException(status_code=400, detail="Email already registered")
    return user_crud.create(db, obj_in=payload)


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    """Partially update an existing user."""
    user = get_user(db, user_id)
    return user_crud.update(db, db_obj=user, obj_in=payload)


def delete_user(db: Session, user_id: int) -> User:
    """Delete a user by ID."""
    user = user_crud.delete(db, obj_id=user_id)
    if not user:
        raise NotFoundException(detail=f"User {user_id} not found")
    return user


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def authenticate_user(db: Session, email: str, password: str) -> Token:
    """Validate credentials and return a JWT ``Token``."""
    user = user_crud.get_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        raise AppException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)
