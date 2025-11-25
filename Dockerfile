FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy fixed octoparse library (with bug fixes)
COPY octoparse_fixed.py /usr/local/lib/python3.11/site-packages/octoparse/octoparse.py

# Copy app files
COPY *.py .

# Copy credentials (mount these as volumes in production)
# COPY .env .
# COPY client_secret.json .
# COPY token.json .

CMD ["python", "main.py"]
