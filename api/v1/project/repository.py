from dotenv import load_dotenv
from fastapi import UploadFile , File,Depends
from sqlalchemy.orm import Session
from utils.file import FileUtils
from .model import Project
from core.deps import get_db
import boto3
import os
from dotenv import load_dotenv
from .schema import FileExtract
load_dotenv()

from .schema import ProjectCreate , CategoryIn
class ProjectRepository:
    def __init__(self):
        self.__file_utils = FileUtils()
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),  
        )
        self.bucket_name = os.environ.get("BUCKET_NAME")
    
    async def create_project(self, project_name : str,category_id :int,files: UploadFile = File(...),db : Session = Depends(get_db)) :
        file_name = self.__file_utils.upload_file(files)
        new_project = Project(
            project_name=project_name,
            document_url=file_name, 
            category_id=category_id )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return new_project
    
    def get_project(self, category_id : CategoryIn , db : Session = Depends(get_db)):

        project = db.query(Project).filter(Project.category_id == category_id.category_id).all()
    
        return project
    def extract_text_from_file(self,file_name: FileExtract):
        try:
            # Download file from S3
            print(file_name.file_name)
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_name.file_name)
            extract_text = response['Body'].read().decode('latin-1')
            print(extract_text)
            return {"extracted_text": extract_text}
        except Exception as e:
            return {"extracted_text": str(e)}

            