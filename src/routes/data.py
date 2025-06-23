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
from models.db_schemes import DataChunk

logger = logging.getLogger("uvicorn.error")



data_router=APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(request:Request, project_id: str, file: UploadFile,
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

    return JSONResponse(
        content={
            "message": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
            "file_id": file_id
        }
    )

# this is the endpoint to process the file and save the chunks to the database
# it will be called after the file is uploaded successfully
@data_router.post("/process/{project_id}")
async def process_data(req:Request,project_id: str, request: ProcessRequest):
    file_id = request.file_id
    chunk_size = request.chunk_size
    overlap_size = request.overlap_size
    do_reset = request.do_reset


    project_model = await ProjectModel.create_instance(req.app.db_client) # get the project model from the request app's db_client

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    

    process_controller = ProcessController(project_id)
    file_content = process_controller.get_file_content(file_id)

    
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap=overlap_size
    )

    
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponseSignal.PROCESSING_FAILED.value,
            }
        )
    
    # save the chunks to the database
    file_chunks_records = [
        DataChunk(
            chunk_text = chunk.page_content,
            chunk_meatadata= chunk.metadata,
            chunk_order = i+1, 
            chunk_project_id= project.id
        )
        for i, chunk in enumerate(file_chunks)
        ]
    chunk_model = await ChunkModel.create_instance(req.app.db_client)


    if do_reset == 1 :
        # delete all the chunks for the project if do_reset is set to 1 and if the project exists
        no_of_deleted_chunks = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )
        logger.info(f"Deleted {no_of_deleted_chunks} chunks for project {project_id}")

    
    no_of_recoreds = await chunk_model.insert_many_chunks(
        chunks=file_chunks_records,
    )
    return JSONResponse(
        content={
            "message": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_of_recoreds
        }
    )

# stateless applications you do not save any data.
# statefull applications you save data in the database or in the file system.

