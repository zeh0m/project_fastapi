from celery import Celery
from sqlalchemy.orm import Session
from models import Document, DocumentsText
from database import Sessionlocal
import pytesseract
from PIL import Image
import logging
import cv2
import numpy as np

celery_app= Celery("worker", broker="amqp://guest:guest@localhost:5672//")




@celery_app.task()
def analyse_document_task(doc_id: int):
    db: Session = Sessionlocal()
    try:
        document = db.query(Document).filter(Document.id == doc_id).one_or_none()
        if not document:
            logging.error(f"Document with id {doc_id} not found")
            return

        # Открываем изображение
        img = Image.open(document.path)
        img = img.convert("RGB")
        img_cv = np.array(img)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)


        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)


        sharpen_kernel = np.array([[-1, -1, -1],
                                   [-1,  9, -1],
                                   [-1, -1, -1]])
        sharp = cv2.filter2D(gray, -1, sharpen_kernel)


        _, thresh = cv2.threshold(sharp, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Конфиг для Tesseract
        custom_config = r'--oem 3 --psm 6'


        text = pytesseract.image_to_string(thresh, lang='eng', config=custom_config)


        doc_text = DocumentsText(doc_id=doc_id, text=text)
        db.add(doc_text)
        db.commit()

        logging.info(f"Document {doc_id} processed successfully.")

    except Exception as e:
        logging.exception(f"Error processing document {doc_id}: {e}")
        db.rollback()
    finally:
        db.close()




