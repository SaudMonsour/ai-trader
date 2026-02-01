FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for pandas/numpy compilation)
# RUN apt-get update && apt-get install -y gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download TextBlob corpora
RUN python -m textblob.download_corpora

COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/main.py"]
