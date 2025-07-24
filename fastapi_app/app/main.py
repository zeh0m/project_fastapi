import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
import logging


from app import models
from app.database import Sessionlocal
from app.celery_worker import analyse_document_task
from app.models import Document
from app.schemas import AnalyseRequest

app = FastAPI()

DocumentFolder = "app/documents/images"
os.makedirs(DocumentFolder, exist_ok=True)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


if not os.path.exists(DocumentFolder):
    os.makedirs(DocumentFolder)

@app.post("/upload_doc", summary="Upload document", description="We will load the document into the hard drive and db")
async def upload_document(
    file: UploadFile = File(...),
    path: str = Form(...),
    filename: str = Form(...),
    db: Sessionlocal = Depends(get_db)
):
    try:
        file_path = os.path.join(DocumentFolder, filename)

        os.makedirs(path, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        document = Document(
            filename=filename,
            path=file_path
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return {
            "message": "file uploaded",
            "doc_id": document.id,
            "filename": filename,
            "saved_path": file_path
        }

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
def analyse_document(payload: AnalyseRequest, db: Sessionlocal = Depends(get_db)):
    doc_id = payload.doc_id
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





























