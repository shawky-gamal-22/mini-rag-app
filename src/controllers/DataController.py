from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
from .ProjectController import ProjectController
import re
import os

class DataController(BaseController):

    def __init__(self):
        super().__init__()


    def validate_uploaded_file(self, file: UploadFile) -> bool:
        """
        Validate the uploaded file based on the application settings.
        """

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_ALLOWED
        if file.size > self.app_settings.FILE_MAX_SIZE:
            return False, ResponseSignal.FILE_SIZE_EXCEEDS_LIMIT
        
        return True, ResponseSignal.FILE_VALIDATED_SUCCESS
        
    
    def generate_unique_filename(self, original_filename: str, project_id: str) -> str:
        """
        Generate a unique filename for the uploaded file.
        """
        random_filename = self.generate_random_string(10)

        project_path = ProjectController().get_project_path(project_id)

        cleaned_filename = self.get_clean_file_name(original_filename)
        unique_filename = f"{random_filename}_{cleaned_filename}"

        new_file_path = os.path.join(project_path, unique_filename)

        # Ensure the file does not already exist
        while os.path.exists(new_file_path):
            random_filename = self.generate_random_string(10)
            unique_filename = f"{random_filename}_{cleaned_filename}"
            new_file_path = os.path.join(project_path, unique_filename)
        return new_file_path

    def get_clean_file_name(self, orig_filename:str) -> str:

        # Clean the original filename by removing unwanted characters
        # and replacing spaces with underscores.
        cleaned_filename = re.sub(r'[^\w.]','', orig_filename.strip())
        cleaned_filename = cleaned_filename.replace(' ', '_')

        return cleaned_filename
    


