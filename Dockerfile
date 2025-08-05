FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PORT=8080
ENV DATABASE_URL=postgresql://neondb_owner:npg_Ytxmwd1Tr4VC@ep-empty-shadow-ad03u12w-pooler.c-2.us-east-1.aws.neon.tech/financial_analysis_system?sslmode=require&channel_binding=require

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthy || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]