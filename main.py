import os
import base64
from models import DocumentsText
import pytesseract
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File

from PIL import Image

import models
import schemas
from database import engine, Sessionlocal
import logging
from celery_worker import analyse_document_task
from models import DocumentsText

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

DocumentFolder = "documents"
os.makedirs(DocumentFolder, exist_ok=True)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


DocumentFolder = "documents"

if not os.path.exists(DocumentFolder):
    os.makedirs(DocumentFolder)

@app.post("/upload_doc", summary="Upload document", description="We will load the document into the hard drive and db")
async def upload_document(file: UploadFile = File(...), db: Sessionlocal = Depends(get_db)):
    file_path = os.path.join(DocumentFolder, file.filename)

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        document = models.Document(filename=file.filename, path=file_path)
        db.add(document)
        db.commit()
        db.refresh(document)

        return {"message": "file uploaded", "doc_id": document.id}

    except Exception as e:
        db.rollback()
        logging.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading document: {e}")



@app.delete("/delete_doc/{doc_id}", summary="Delete document", description="We will delete the document from the hard drive and db")
def delete_document(doc_id: int, db: Sessionlocal = Depends(get_db)):
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        if os.path.isfile(document.path):
            os.remove(document.path)
        else:
            logging.warning(f"File {document.path} not found.")
    except Exception as e:
        logging.error(f"Error deleting file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

    try:
        db.delete(document)
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")
    return {"message": "file deleted"}

@app.post("/doc_analyse", summary="Analyse document", description="We will analyse the document in db")
def analyse_document(doc_id: int, db: Sessionlocal = Depends(get_db)):
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    analyse_document_task.delay(doc_id)
    return {"message": "file send to celery"}


@app.get("/get_text", summary="Get text", description="We will get the text from the db")
def get_document_text(doc_id: int, db: Sessionlocal = Depends(get_db)):
    document_text = db.query(models.DocumentsText).filter(models.DocumentsText.doc_id == doc_id).first()

    if not document_text:
        raise HTTPException(status_code=404, detail="Text not found")

    return {
        "id": document_text.id,
        "text": document_text.text
    }





























