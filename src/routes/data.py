from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
#from controllers.DataController import DataController
from controllers import DataController, ProjectController, ProcessController # i have imported the datacontroller in the __init_.py file in the controllers folder so i can import it like this
import aiofiles
from models import ResponseSignal
import logging 
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk, Asset
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnum import AssetTypeEnum
from bson import ObjectId
from controllers import NLPController
from tasks.file_processing import process_project_files
from tasks.process_workflow import process_and_push_workflow


logger = logging.getLogger("uvicorn.error")



data_router=APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(request:Request, project_id: int, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):

    project_model = await ProjectModel.create_instance(request.app.db_client) # get the project model from the request app's db_client

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

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
    file_path, file_id = data_controller.generate_unique_filepath(file.filename, project_id)

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
    
    # create an asset record in the database
    asset_model = await AssetModel.create_instance(request.app.db_client)
    asset_resource = Asset(
        asset_project_id= project.project_id,
        asset_type= AssetTypeEnum.FILE.value,
        asset_name= file_id,
        asset_size= os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset_resource)
    logger.info(f"File {file.filename} uploaded successfully to {file_path}")

    return JSONResponse(
        content={
            "message": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
            "file_id": str(asset_record.asset_id)
        }
    )

# this is the endpoint to process the file and save the chunks to the database
# it will be called after the file is uploaded successfully
@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: int, process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    task = process_project_files.delay(
        project_id= project_id,
        file_id = process_request.file_id,
        chunk_size= chunk_size,
        overlap_size= overlap_size,
        do_reset= do_reset,

    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_PROCESSING_SUCCESS.value,
            "task_id": task.id
        }
    )

   

# stateless applications you do not save any data.
# statefull applications you save data in the database or in the file system.

@data_router.post("/process-and-push/{project_id}")
async def process_and_push(request: Request, project_id: int, process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    workflow_task = process_and_push_workflow.delay(
        project_id= project_id,
        file_id = process_request.file_id,
        chunk_size= chunk_size,
        overlap_size= overlap_size,
        do_reset= do_reset,

    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESS_AND_PUSH_WORKFLOW_READY.value,
            "workflow_task_id": workflow_task.id
        }
    )