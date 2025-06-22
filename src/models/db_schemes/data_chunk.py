from pydantic import BaseModel, Field, validator
from bson.objectid import ObjectId
from typing import Optional

class DataChunk(BaseModel):
        
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_meatadata: dict 
    chunk_order: int = Field(..., gt=0)  # Ensures chunk_order is a positive integer
    chunk_project_id: ObjectId



    class Config:
        arbitrary_types_allowed = True # Allows ObjectId to be used





    
