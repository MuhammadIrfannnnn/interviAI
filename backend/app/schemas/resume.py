from pydantic import BaseModel
from typing import List

class ParsedResume(BaseModel):
    name:str | None=None
    email:str | None=None
    skills:List[str]=[]
    education:List[str]=[]
    projects:List[str]=[]
    experience:List[str]=[] 