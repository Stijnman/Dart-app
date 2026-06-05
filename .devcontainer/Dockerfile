# Dart Game Pro Dev Container
# Based on official Python dev container

FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        git \
        curl \
        build-essential \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspaces/Dart-app

# Copy requirements first for better caching
COPY requirements.txt* ./

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt || true

# Install additional useful packages for Streamlit development
RUN pip install \
    streamlit \
    plotly \
    pandas \
    numpy \
    matplotlib \
    black \
    pylint

# Expose Streamlit default port
EXPOSE 8501

# Default command (can be overridden)
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]