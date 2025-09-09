#!/bin/bash
set -e
echo "Installing system dependencies..."
apt-get update -y
apt-get install -y ffmpeg libavdevice-dev wget unzip

echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Download Vosk models (English/Hindi/Gujarati) if not present
if [ ! -d "vosk-model-small-en-in" ]; then
  echo "Downloading Vosk English (IN) model..."
  wget https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip -O vosk-en.zip
  unzip vosk-en.zip
  mv vosk-model-small-en-in-0.4 vosk-model-small-en-in || true
  rm vosk-en.zip
fi

if [ ! -d "vosk-model-hi-in" ]; then
  echo "Downloading Vosk Hindi model..."
  wget https://alphacephei.com/vosk/models/vosk-model-hi-in-0.4.zip -O vosk-hi.zip
  unzip vosk-hi.zip
  mv vosk-model-hi-in-0.4 vosk-model-hi-in || true
  rm vosk-hi.zip
fi

if [ ! -d "vosk-model-gu-in" ]; then
  echo "Downloading Vosk Gujarati model..."
  wget https://alphacephei.com/vosk/models/vosk-model-gu-in-0.4.zip -O vosk-gu.zip
  unzip vosk-gu.zip
  mv vosk-model-gu-in-0.4 vosk-model-gu-in || true
  rm vosk-gu.zip
fi

echo "Launch Streamlit app..."
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
