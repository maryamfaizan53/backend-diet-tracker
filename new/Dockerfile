FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Add curl for HEALTHCHECK and tools for building some wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Optional: healthcheck uses PORT if set, fallback to 8000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD sh -c 'PORT=${PORT:-8000}; curl -f http://localhost:$PORT/health || exit 1'

# Use shell form so ${PORT} is expanded at container start
CMD sh -c 'uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --loop asyncio'



# # docker
# FROM python:3.10-slim
# WORKDIR /app
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# EXPOSE 8000
# HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]
