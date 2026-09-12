import bcrypt
from application.user import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    def __init__(self, rounds: int = 12):
        self._rounds = rounds

    def hash(self, plain_password: str) -> str:
        salt = bcrypt.gensalt(rounds=self._rounds)
        hashed_bytes = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed_bytes.decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except TypeError:
            return False
