from typing import List
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base


class Document(Base):
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(unique=True, index=True)
    path: Mapped[str] = mapped_column()

    text_entries: Mapped[List["DocumentsText"]] = relationship(
        back_populates="document",
        cascade="all, delete",
        passive_deletes=True
    )


class DocumentsText(Base):
    __tablename__ = 'documents_text'
    id: Mapped[int] = mapped_column(primary_key=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey('document.id', ondelete="CASCADE"))
    text: Mapped[str] = mapped_column()

    document: Mapped["Document"] = relationship(back_populates="text_entries")
