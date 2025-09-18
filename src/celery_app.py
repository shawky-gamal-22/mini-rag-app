from celery import Celery 
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

settings = get_settings()

async def get_setup_utils():
    settings = get_settings()

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    db_engine = create_async_engine(postgres_conn)

    db_client = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit = False,

    )

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory= VectorDBProviderFactory(config=settings,
                                                       db_client=db_client)

    # generation client
    generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    generation_client.set_generation_model(model_id= settings.GENERATION_MODEL_ID)

    # embedding_client
    embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size= settings.EMBEDDING_MODEL_SIZE)
    
    # vectordb client
    vectordb_client = vectordb_provider_factory.create(
        provider= settings.VECTOR_DB_BACKEND
    )
    await vectordb_client.connect()


    template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG
    )

    return (db_engine, db_client, llm_provider_factory, vectordb_provider_factory,
            generation_client, embedding_client, vectordb_client, template_parser)

# Create celery app instance
celery_app = Celery(
    'minirag',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.file_processing",
        "tasks.data_indexing",
        "tasks.process_workflow"
    ]

)

# Configure clerey with essential settngs

celery_app.conf.update(
    task_serializer= settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=[
        settings.CELERY_TASK_SERIALIZER
    ],
    task_acks_late= settings.CELERY_TASK_ACKS_LATE,
    task_time_limit= settings.CELERY_TASK_TIME_LIMIT,
    task_ignore_result= False,
    result_expires=3600, 
    worker_concurrency= settings.CELERY_WORKER_CONCURRENCY,

    # Connection settings for better reliability
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    worker_cancel_long_running_tasks_on_connection_loss=True,

    task_routes={
        "tasks.file_processing.process_project_files":{"queue":"file_processing"},
        "task.data_indexing.index_data_content":{"queue":"data_indexing"},
        "tasks.tasks.process_workflow.process_and_push_workflow":{"queue":"file_processing"}
    }
)
celery_app.conf.task_default_queue = "default"