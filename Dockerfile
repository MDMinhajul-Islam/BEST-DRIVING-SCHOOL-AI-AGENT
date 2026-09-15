FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 BOOKING_MODE=mock BOOKING_DB_PATH=/app/runtime/booking.sqlite3
COPY requirements.deploy.txt .
RUN pip install --no-cache-dir -r requirements.deploy.txt && useradd --uid 10001 --create-home booking
COPY config ./config
COPY src ./src
COPY data/structured/package_catalog.json data/structured/internal_business_scheduling_rules.json ./data/structured/
RUN mkdir -p /app/runtime && chown -R booking:booking /app/runtime
USER booking
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"
CMD ["uvicorn", "src.routes.booking:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log"]
