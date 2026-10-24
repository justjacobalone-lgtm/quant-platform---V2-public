FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080 SHADOW_RESULTS_PATH=/tmp/shadow-results.jsonl ALLOW_LIVE_TRADING=false TRADING_MODE=SHADOW
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY dashboard ./dashboard
COPY research ./research
COPY shadow ./shadow
COPY strategies ./strategies
COPY deploy/start-web.sh ./start-web.sh
RUN chmod 755 /app/start-web.sh && useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser
CMD ["/app/start-web.sh"]
