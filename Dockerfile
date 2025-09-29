
# syntax=docker/dockerfile:1
FROM python:3.13.3-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir "uvicorn[standard]" jupyter

# Copy the rest of your app
COPY . .

# Expose ports
EXPOSE 8000 3001

# Run both Uvicorn and Jupyter Lab
# Uvicorn runs in the background, Jupyter runs in the foreground
CMD ["sh", "-c", "\
    uvicorn backend:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 1800 & \
    jupyter lab --ip=0.0.0.0 --NotebookApp.token='' --NotebookApp.password='' --port=3001 --no-browser --allow-root \
"]


