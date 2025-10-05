#!/bin/bash

# ==============================================================================
# AI YASHVI COLAB LAUNCH SCRIPT
# This script sets up the environment and runs the dual-service architecture:
# 1. FastAPI (app.py) for LLM/TTS processing (backend)
# 2. Streamlit (yashvi_bot_streamlit.py) for the user interface (frontend)
# ==============================================================================

# --- 1. Install System Dependencies ---
# These are necessary for compiling certain Python packages (like sentencepiece or gtts dependencies)
echo "--- 1. Installing required system packages (cmake, pkg-config) ---"
apt-get update -qq
# Using -qq for quiet update, > /dev/null 2>&1 to suppress excessive output
apt-get install -y cmake pkg-config > /dev/null 2>&1

# --- 2. Install Python Dependencies ---
echo "--- 2. Installing Python dependencies from requirements.txt ---"
pip install -r requirements.txt

# Define the Streamlit file name (assumed from previous steps)
STREAMLIT_FILE="yashvi_bot_streamlit.py"

# --- 3. Start FastAPI Backend (app.py) ---
# Running on port 8000 in the background (using nohup)
echo "--- 3. Starting FastAPI backend (app.py) on http://127.0.0.1:8000 ---"
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > fastapi_log.txt 2>&1 &
BACKEND_PID=$!
echo "FastAPI process started with PID: $BACKEND_PID. Check fastapi_log.txt for details."

# Give the backend a moment to start up before the frontend tries to connect
sleep 5

# --- 4. Start Streamlit Frontend ---
# Running Streamlit in the foreground, typically on port 8501
# Colab or hosting services usually handle the tunneling/URL exposure automatically
echo "--- 4. Starting Streamlit frontend ($STREAMLIT_FILE) on port 8501 ---"

if [ -f "$STREAMLIT_FILE" ]; then
    streamlit run "$STREAMLIT_FILE" \
        --server.port 8501 \
        --server.enableCORS false \
        --server.enableXsrfProtection false
else
    echo "ERROR: Streamlit frontend file '$STREAMLIT_FILE' not found!"
    echo "Please ensure this file is present in the directory."
    # Attempt to kill the background FastAPI process on error
    kill $BACKEND_PID
fi

# Cleanup: This block is often reached only if Streamlit is manually stopped.
echo "Script finished."

# Note: The FastAPI server (PID: $BACKEND_PID) may need to be manually stopped 
# in the Colab notebook interface if the Streamlit script exits unexpectedly.
