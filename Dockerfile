# --- Stage 1: Build and install dependencies ---
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system tools needed to compile some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the file needed for installation to protect the cache
COPY flask_app/requirements.txt .

# Install dependencies into a specific folder and clear the pip cache
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Final lightweight runtime image ---
FROM python:3.10-slim

WORKDIR /app

# Copy the pre-installed Python packages from the builder stage
COPY --from=builder /install /usr/local

# Download NLTK data directly into the shared folder
RUN python -m nltk.downloader -d /usr/local/share/nltk_data stopwords wordnet

# Copy your actual application files and models
COPY flask_app/ /app/
COPY models/vectorizer.pkl /app/models/vectorizer.pkl

EXPOSE 5000


#local
# CMD ["python", "app.py"] 

# Production Command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
