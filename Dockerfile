FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Run the server directly from server.app
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
