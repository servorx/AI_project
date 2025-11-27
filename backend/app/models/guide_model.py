from pydantic import BaseModel

class Guide(BaseModel):
    title: str
    content: str
