from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    """
    ProjectModel class for managing project data.
    Inherits from BaseDataModel.
    This class provides methods to interact with project data in the database.
    """
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]


    async def create_project(self, project: Project) -> Project:
        """
        Create a new project in the database.
        
        :param project: Project object to be created.
        :return: Created Project object.
        """
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True)) # insert_one returns an InsertOneResult object and takes a dictionary
        # without await it will return a coroutine object
        project._id = result.inserted_id # inserted_id is the id of the inserted document
        return project
        
    async def get_project_or_create_one(self, project_id: str):

        record = await self.collection.find_one({
            "project_id": project_id
            }) # any function from motor returns a coroutine object, so we need to await it
        
        if record is None:
            # If no record found, create a new project with the given project_id
            new_project = Project(project_id=project_id)
            project = await self.create_project(new_project)
            return project
        else:
            # If record found, return the existing project
            return Project(**record)
        
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        """
        Get all projects with pagination. pagination means that we will return only a subset of projects
        
        :param page: Page number for pagination.
        :param page_size: Number of items per page.
        :return: List of Project objects.
        """
        # count the total number of documents in the collection
        total_count = await self.collection.count_documents({}) # count_documents returns a coroutine object, so we need to await it and takes a filter like find()

        total_pages = total_count  // page_size  # Calculate total pages
        if total_count % page_size > 0:
            total_pages += 1

        cursor =self.collection.find({}).skip((page - 1) * page_size).limit(page_size)
        projects = []
        async for record in cursor:
            projects.append(Project(**record))

        return projects, total_pages
    
    