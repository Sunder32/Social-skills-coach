FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for models and data
RUN mkdir -p models data

# Expose Gradio port
EXPOSE 7860

# Run the training UI
CMD ["python", "training_ui.py"]
