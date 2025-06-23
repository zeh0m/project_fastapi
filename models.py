from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Document(Base):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    path = Column(String)


class DocumentsText(Base):
    __tablename__ = 'documents_text'
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey('document.id'))
    text = Column(String)
    document = relationship("Document")