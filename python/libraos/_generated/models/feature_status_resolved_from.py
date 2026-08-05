from enum import Enum


class FeatureStatusResolvedFrom(str, Enum):
    DEFAULT = "default"
    ENV = "env"
    SETTING = "setting"

    def __str__(self) -> str:
        return str(self.value)
