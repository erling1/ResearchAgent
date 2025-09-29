#!/bin/bash

# Start Uvicorn in the background
uvicorn backend:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 1800 &

# Start Jupyter Lab in the foreground
jupyter lab \
  --ip=0.0.0.0 \
  --NotebookApp.token='' \
  --NotebookApp.password='' \
  --port=3001 \
  --no-browser \
  --allow-root
