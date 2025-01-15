from pydantic import BaseModel , EmailStr
from datetime import datetime

class UserSchema(BaseModel):
    email : EmailStr
    name : str
    contact_no : str
    password : str
    


class UserOut(BaseModel):
    id : int
    email : EmailStr
    name : str
    contact_no : str
    created_at : datetime
    class Config:
        orm_mode = True