from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException, status

def create_user(db: Session, user_in: UserCreate):
    # 1. Verificar se o usuário já existe
    user_exists = db.query(User).filter(User.email == user_in.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está cadastrado."
        )

    # 2. Criar a instância do modelo (Idealmente, aqui você faria o hash da senha)
    db_user = User(
        email=user_in.email,
        hashed_password=user_in.password + "not-secure-hash", # Exemplo didático
        is_active=True
    )

    # 3. Persistir no banco
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_in: UserUpdate) -> User:
    user = get_user(db, user_id)

    if user_in.email is not None and user_in.email != user.email:
        user_exists = db.query(User).filter(User.email == user_in.email).first()
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este e-mail já está cadastrado."
            )
        user.email = user_in.email

    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    if user_in.password is not None:
        user.hashed_password = user_in.password + "not-secure-hash"

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()