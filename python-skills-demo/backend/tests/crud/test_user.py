"""Unit tests for the User CRUD operations."""

from app.crud.user import user_crud
from app.schemas.user import UserCreate


def test_create_and_get_by_email(db_session):
    """CRUD create hashes the password and get_by_email retrieves the user."""
    user_in = UserCreate(email="test@example.com", password="plain", full_name="Test")
    created = user_crud.create(db_session, obj_in=user_in)

    assert created.id is not None
    assert created.hashed_password != "plain"  # must be hashed

    fetched = user_crud.get_by_email(db_session, email="test@example.com")
    assert fetched is not None
    assert fetched.id == created.id


def test_get_nonexistent(db_session):
    """Getting a user that doesn't exist returns None."""
    assert user_crud.get(db_session, obj_id=9999) is None
