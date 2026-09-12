from dataclasses import dataclass

from application.session.dto import SessionResponseDto
from application.user.dto import UserResponseDto


@dataclass(frozen=True)
class LoginDto:
    email: str
    password: str


@dataclass(frozen=True)
class AuthResponseDto:
    user: UserResponseDto
    session: SessionResponseDto
    access_token: str
