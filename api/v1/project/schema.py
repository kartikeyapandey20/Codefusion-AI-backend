from pydantic import BaseModel
from datetime import datetime
class ProjectCreate(BaseModel):
    project_name : str
    category_id : int
    
class ProjectUpdate(BaseModel):
    project_name : str
    category_id : int
    document_url : str
    created_at : datetime
    
class ProjectOut(BaseModel):
    id : int
    project_name : str
    category_id : int
    document_url : str
    created_at : datetime
    
class CategoryIn(BaseModel):
    category_id : int
    
class FileExtract(BaseModel):
    file_name : str
    
class ExtractedText(BaseModel):
    extracted_text : str