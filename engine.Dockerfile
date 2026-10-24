FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY execution ./execution
COPY risk ./risk
CMD ["python","-m","execution.service"]
