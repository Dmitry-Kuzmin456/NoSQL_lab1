from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4


class UserRole(StrEnum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"


@dataclass
class User:
    name: str
    email: str
    password_hash: str
    role: UserRole
    id: UUID = field(default_factory=uuid4)


