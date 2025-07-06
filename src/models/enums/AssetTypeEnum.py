from enum import Enum

class AssetTypeEnum(Enum):
    """
    Enum for asset types.
    """
    FILE = "file"

    @classmethod
    def list(cls):
        return [asset_type.value for asset_type in cls]