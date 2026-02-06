from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.service.user_service import (
    create_user,
    get_user,
    get_users,
    update_user,
    delete_user,
)
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user_in)


@router.get("/", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def retrieve_user(user_id: int, db: Session = Depends(get_db)):
    return get_user(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def edit_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    return update_user(db, user_id, user_in)


@router.delete("/{user_id}", status_code=204)
def remove_user(user_id: int, db: Session = Depends(get_db)):
    delete_user(db, user_id)