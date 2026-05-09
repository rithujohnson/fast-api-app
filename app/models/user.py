from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str
    hashed_password: str
    role: str

    def is_admin(self) -> bool:
        return self.role == "admin"