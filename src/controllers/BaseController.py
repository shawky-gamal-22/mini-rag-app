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
        
    def generate_random_string(self, length: int = 10) -> str:

        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        