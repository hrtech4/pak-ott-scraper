FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Create output/logs dirs
RUN mkdir -p output logs

# Default: run once (CI mode). Override CMD for daemon mode.
CMD ["python", "main.py", "--once"]
