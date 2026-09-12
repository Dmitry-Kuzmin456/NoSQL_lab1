from pydantic import BaseModel, EmailStr, Field

from application.auth.dto import LoginDto


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["ivan@edu.ru"])
    password: str = Field(..., min_length=1, examples=["secretPassword123"])

    def to_dto(self) -> LoginDto:
        return LoginDto(
            email=str(self.email),
            password=self.password,
        )
