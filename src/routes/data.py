from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
#from controllers.DataController import DataController
from controllers import DataController # i have imported the datacontroller in the __init_.py file in the controllers folder so i can import it like this
from controllers import ProjectController
import aiofiles
from models import ResponseSignal
import logging 


logger = logging.getLogger("uvicorn.error")



data_router=APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    
    data_controller = DataController()
    
    # valdate the file properties --> it is a logic then we will implement it in the controller folder
    is_valid, result_signal = data_controller.validate_uploaded_file(file)
    

    if not is_valid:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "message": result_signal.value,
            }
        )

    # get the project path
    project_dir_path = ProjectController().get_project_path(project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        file.filename,
        project_id
        )



    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponseSignal.FILE_UPLOAD_FAILED.value,
            }
        )

    return JSONResponse(
        content={
            "message": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
            "file_id": file_id
        }
    )

