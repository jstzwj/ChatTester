
from pydantic import BaseModel, Field
from typing import List, Optional

class SourceFile(BaseModel):
    path: str
    type: str

class SourcePos(BaseModel):
    line: int
    col: int

class SourceRange(BaseModel):
    start_pos: Optional[SourcePos]
    end_pos: Optional[SourcePos]

class LineRange(BaseModel):
    start_line: int
    end_line: int

class MethodInfo(BaseModel):
    source: SourceFile
    range: LineRange
    text: str
    name: str
    declaration: str

class ClassInfo(BaseModel):
    source: SourceFile
    range: LineRange
    text: str
    name: str
    fields: str
    methods: List[MethodInfo]
