from pydantic import BaseModel

# Base model - common fields
class NoteBase(BaseModel):
    title: str
    description: str

# Create request model
class NoteCreate(NoteBase):
    pass

# Update request model
class NoteUpdate(NoteBase):
    pass

# Response model (includes id)
class NoteOut(NoteBase):
    id: int

    class Config:
         model_config = {
        "from_attributes": True  # replaces orm_mode=True in Pydantic v2
    }