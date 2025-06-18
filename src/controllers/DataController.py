from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal

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
        