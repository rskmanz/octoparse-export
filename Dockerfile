FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY *.py .

# Copy credentials (mount these as volumes in production)
# COPY .env .
# COPY client_secret.json .
# COPY token.json .

CMD ["python", "main.py"]
