FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
# 如果你没有 requirements.txt，可以这样写：
# RUN pip install --no-cache-dir fastapi uvicorn openpyxl pandas python-multipart

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]