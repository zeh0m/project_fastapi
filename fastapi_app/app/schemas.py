from pydantic import BaseModel

class DocumentCreate(BaseModel):
    content_base64: str
    filename: str

class AnalyseRequest(BaseModel):
    doc_id: int