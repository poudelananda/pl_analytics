#!/bin/bash

# --- CONFIGURATION ---
PYTHON_BIN="/Users/m33210/opt/anaconda3/bin/python"
SCRIPT_PATH="/Users/m33210/Desktop/Anandas Documents/AP Projects/soccer_analytics/etl-pipeline/fb_scraper.py"
LOG_DIR="/Users/m33210/Desktop/Anandas Documents/AP Projects/soccer_analytics/logs"
LOG_FILE="$LOG_DIR/fb_scraper.log"

# Create the log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Timestamp for each run
echo "========================================" >> "$LOG_FILE"
echo "Run started: $(date)" >> "$LOG_FILE"

# Run the Python script
$PYTHON_BIN "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Log completion
if [ $EXIT_CODE -eq 0 ]; then
    echo "Run completed successfully at $(date)" >> "$LOG_FILE"
else
    echo "Run FAILED with exit code $EXIT_CODE at $(date)" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"

