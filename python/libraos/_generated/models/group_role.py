from enum import Enum


class GroupRole(str, Enum):
    APPROVER = "approver"
    LEAD = "lead"
    MEMBER = "member"

    def __str__(self) -> str:
        return str(self.value)
