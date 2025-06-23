from enum import Enum


class DataBaseEnum(Enum):
    """
    Enum for database types.
    """
    COLLECTION_PROJECT_NAME = "projects"
    COLLECTION_CHUNK_NAME = "chunks"
    COLLECTION_ASSET_NAME = "assets"