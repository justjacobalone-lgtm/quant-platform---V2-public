FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY strategies ./strategies
COPY shadow ./shadow
COPY research ./research
CMD ["python","-m","shadow.worker"]
