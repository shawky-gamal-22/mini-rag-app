from helpers.config import get_settings, Settings
import os
import random 
import string

class BaseController:
    
    def __init__(self):
        self.app_settings: Settings = get_settings()

        self.base_dir = os.path.dirname(os.path.dirname(__file__)) # Get the parent directory of the current file
        self.file_dir = os.path.join(
            self.base_dir,
            "assets/files"
            )  # Construct the file directory path
        

        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )
        
    def generate_random_string(self, length: int = 10) -> str:

        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        
    def get_database_path(self, db_name:str):

        database_path = os.path.join(
            self.database_dir,
            db_name
        )

        if not os.path.exists(database_path):
            os.makedirs(database_path)
        
        return database_path