FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple

COPY . .

RUN mkdir -p /app/uploads/certificates /app/uploads/contracts /app/uploads/photos /app/uploads/evidence /app/uploads/signatures

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
