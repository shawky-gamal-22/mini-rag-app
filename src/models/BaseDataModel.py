from helpers.config import get_settings

class BaseDataModel:
    """
    Base class for data models.
    This class should be inherited by all data model classes.
    It provides a common interface and basic functionality.
    """

    def __init__(self, db_client: object):
        self.db_client = db_client
        self.app_settings = get_settings()