from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class LoginSchema(BaseModel):
    email: EmailStr
    password: str
    
    
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

class Config:
    orm_mode = True