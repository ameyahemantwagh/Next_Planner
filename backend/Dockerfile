FROM python:3.11-slim

WORKDIR /app

# system deps for common packages
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# copy requirements and install once at build time
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# copy app source
COPY . /app

EXPOSE ${BACKEND_PORT}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${BACKEND_PORT}", "--reload"]