from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if self.email is None and self.is_active is None and self.password is None:
            raise ValueError("Informe ao menos um campo para atualizar.")
        return self

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Permite ler modelos do SQLAlchemy