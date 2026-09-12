from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Хэшировать пароль."""
        raise NotImplementedError

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль на соответствие хэшу."""
        raise NotImplementedError
