# Dockerfile for MaternalMind AI Pregnancy Wellness Platform

# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libsndfile1 \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with specific versions for TensorFlow compatibility
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    streamlit \
    pandas \
    numpy \
    plotly \
    fpdf \
    Pillow \
    scikit-learn \
    bcrypt \
    python-dotenv \
    sqlalchemy \
    alembic \
    python-multipart \
    pydantic \
    python-dateutil \
    pyyaml \
    joblib \
    scipy \
    librosa \
    soundfile \
    pydub \
    && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir tensorflow tensorflow-io

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/models /app/logs /app/backups

# Create non-root user for security
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app
USER streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]