FROM python:3.10-slim

WORKDIR /app

RUN apt update && apt -y upgrade && apt -y install \
    tesseract-ocr \
    tesseract-ocr-rus \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt


RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt -y upgrade && apt -y install tesseract-ocr tesseract-ocr-rus

COPY . /app





