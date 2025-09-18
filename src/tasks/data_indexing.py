from celery_app import celery_app, get_setup_utils
from helpers.config import get_settings
import asyncio
from models import ResponseSignal
import logging 
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models import ResponseSignal
from controllers import NLPController
import logging
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)

@celery_app.task(
        bind=True, name="tasks.data_indexing.index_data_content",
        autoretry_for = (Exception,),
        retry_kwargs={"max_retries": 3, "countdown": 60}
)
def index_data_content(self, project_id: int, do_reset:int):

    return asyncio.run(_index_data_content(
        self,
        project_id,
        do_reset
    ))


async def _index_data_content(task_instance, project_id: int, do_reset:int):

    db_engine, vectordb_client = None, None

    try:
    
        (db_engine, db_client, llm_provider_factory, vectordb_provider_factory,
                generation_client, embedding_client, vectordb_client, template_parser) = await get_setup_utils()

        logger.info(f"Setup utils were loaded!")

        project_model = await ProjectModel.create_instance(db_client) # get the project model from the request app's db_client

        chunk_model = await ChunkModel.create_instance(
            db_client = db_client
        )

        project = await project_model.get_project_or_create_one(
            project_id=project_id
        )


        if not project :

            task_instance.update_state(
                state="FAILURE",
                meta={
                    'signal': ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
                }
            )

            raise Exception(f"No project found for project_id: {project_id}")
        
        nlp_controller = NLPController(
            vectordb_client= vectordb_client,
            generation_client= generation_client,
            embedding_client= embedding_client,
            template_parser= template_parser
        )

        has_records = True
        page_no = 1
        inserted_items_count =0
        idx= 0


        # create collection if not exists
        collection_name = nlp_controller.create_collection_name(project_id=project.project_id)

        _ = await vectordb_client.create_collection(
            collection_name = collection_name,
            embedding_size= embedding_client.embedding_size,
            do_reset = do_reset,

        )
        

        # setup batching 

        total_chunks_count = await chunk_model.get_total_chunks_count(project_id=project.project_id)
        pbar = tqdm(total=total_chunks_count, desc="Vector Indexing", position=0)


        while has_records:

            page_chunks = await chunk_model.get_project_chunks(project_id= project.project_id,page_no=page_no)

            if len(page_chunks):
                page_no +=1

            if (not page_no) or (len(page_chunks) ==0) :
                has_records = False
                break

            chunks_ids = [ c.chunk_id for c in page_chunks ]
            idx += len(page_chunks)

            is_inserted = await nlp_controller.index_into_vector_db(
                chunks_ids= chunks_ids,
                project= project,
                chunks=page_chunks,
            )

            if not is_inserted:

                task_instance.update_state(
                    state="FAILURE",
                    meta={
                        'signal': ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                    }
                )

                
                raise Exception(f"can not insert into vectorDB | project_id: {project_id}")

            pbar.update(len(page_chunks))
            inserted_items_count += len(page_chunks)

        
        task_instance.update_state(
                    state="SUCCESS",
                    meta={
                        'signal': ResponseSignal.INSERT_INTO_VECTORDB_SUCCES.value
                    }
                )
        
        
        return{
                "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCES.value,
                "inserted_items_counts": inserted_items_count
              }
        

    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise
    finally:
        try:
            if db_engine:
                await db_engine.dispose()

            if vectordb_client:
                await vectordb_client.disconnect()

        except Exception as e :
            logger.error(f"Task failed while cleaning: {str(e)}")





