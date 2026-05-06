from enum import Enum


class UserCreateRole(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    EMPLOYEE = "employee"
    MANAGER = "manager"

    def __str__(self) -> str:
        return str(self.value)
