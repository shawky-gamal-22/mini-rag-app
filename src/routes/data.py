from fastapi import FastAPI, APIRouter, Depends, UploadFile
import os
from helpers.config import get_settings, Settings
#from controllers.DataController import DataController
from controllers import DataController # i have imported the datacontroller in the __init_.py file in the controllers folder so i can import it like this


data_router=APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    
    # valdate the file properties --> it is a logic then we will implement it in the controller folder
    is_valid, result_signal = DataController().validate_uploaded_file(file)
    

    return {
        "is_valid": is_valid,
             "result_signal": result_signal,
             "project_id": project_id,
             "file_name": file.filename
             }


