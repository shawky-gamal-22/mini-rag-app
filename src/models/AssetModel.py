from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):
    """
    AssetModel class for managing asset data.
    Inherits from BaseDataModel.
    This class provides methods to interact with asset data in the database.
    """
    
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        """
        Factory method to create an instance of ProjectModel.
        
        :param db_client: Database client object.
        :return: Instance of ProjectModel.
        """
        instance = cls(db_client)
        await instance.init_collection()

        return instance
        
    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collection:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()  # Get indexes from the Project model
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index.get("unique", False)  # Use unique if specified, otherwise default to False
                )

    
    async def create_asset(self, asset: Asset)-> Asset: 
        """
        Create a new asset in the database.
        
        :param asset: Asset object to be created.
        :return: The created asset object.
        """
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset

    async def get_all_project_assets(self, asset_project_id: str):
        """
        Get all assets for a specific project.
        
        :param project_id: The ID of the project to retrieve assets for.
        :return: A list of Asset objects associated with the project.
        """
        cursor = self.collection.find({"asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id})
        assets = []
        async for document in cursor:
            asset = Asset(**document)
            assets.append(asset)
        return assets
