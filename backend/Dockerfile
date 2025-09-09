FROM python:3.12-slim

# Set working directory
WORKDIR /app


# Install system deps (just in case any wheels need build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY geoip_lookup.py .

# Create directory for MMDB files
RUN mkdir -p /tmp

# Expose the port
EXPOSE 6970

# Run the application with uvicorn
CMD ["uvicorn", "geoip_lookup:app", "--host", "0.0.0.0", "--port", "6970", "--workers", "1"]
