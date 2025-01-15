from .repository import ProjectRepository

class ProjectDomain:
    
    def __init__(self) -> None:
        self.__repository = ProjectRepository()

    async def create_project(self, project_name , category_id , file,db):
        return await self.__repository.create_project(project_name , category_id , file,db)
    
    def get_projects(self, category_id,db):
        return self.__repository.get_project(category_id, db)
    
    def extract_text_from_file(self,file_name):
        return self.__repository.extract_text_from_file(file_name)