from .domain import ProjectDomain
from fastapi import APIRouter
from fastapi import File, UploadFile , Depends
from .schema import ProjectCreate ,ProjectUpdate , ProjectOut , CategoryIn , FileExtract,ExtractedText
from sqlalchemy.orm import Session
from core.deps import get_db
from typing import List
class ProjectRouter():
    def __init__(self) -> None:
        self.__domain = ProjectDomain()
        
    @property
    def router(self):
        api_router = APIRouter(prefix="/project", tags=["project"])
        
        @api_router.post("/",response_model=ProjectUpdate)
        async def create_project(project_name : str, category_id : int , files: UploadFile = File(...),db :Session =  Depends(get_db)):
            return await self.__domain.create_project(project_name , category_id ,files,db)
        
        @api_router.post("/category_wise", response_model=List[ProjectOut])
        def get_projects(category_id : CategoryIn , db : Session = Depends(get_db)):
            return self.__domain.get_projects(category_id, db)

        @api_router.post("/extract_text_from_file",response_model=ExtractedText)
        def extract_text_from_file(file_name : FileExtract):
            return self.__domain.extract_text_from_file(file_name)
        return api_router