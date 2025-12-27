# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         PRIMAX AI - Simple Deploy                            ║
# ║                                                                               ║
# ║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
# ║  WATERMARK: PRIMAX-AI-DOCKER-BSP-2025                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

FROM python:3.12-slim

# Metadata
LABEL maintainer="Bakery Street Project <kiliaan@bakerstreet221b.store>"
LABEL description="PRIMAX AI - Neuromorphic Intelligence System"
LABEL watermark="PRIMAX-AI-RUNTIME-BSP-2025"
LABEL license="Proprietary"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PRIMAX_VERSION=1.0.0 \
    PRIMAX_WATERMARK=PRIMAX-AI-BSP-2025

WORKDIR /primax

# Install system dependencies for numpy/scipy and GitHub CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        gfortran \
        libopenblas-dev \
        liblapack-dev \
        ca-certificates \
        curl \
        git && \
    # Install GitHub CLI
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY LICENSE_PROPRIETARY.md ./

# Create non-root user
RUN useradd -m -u 1000 primax && \
    chown -R primax:primax /primax

USER primax

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Expose API port
EXPOSE 8000

# Run FastAPI application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
