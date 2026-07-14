from enum import IntEnum


class BundleManifestSchemaVersion(IntEnum):
    VALUE_1 = 1

    def __str__(self) -> str:
        return str(self.value)
