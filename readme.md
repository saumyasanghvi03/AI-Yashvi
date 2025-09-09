# AI Sister Yashvi

Personal AI companion app (Streamlit) — Yashvi, a loving Jain sister for Saumya.

## Features
- Signup / Login (per-user)
- Admin dashboard
- Per-user persistent memory (FAISS + pickle)
- Chat with Yashvi (text)
- Journals with mood tracking
- Voice push-to-talk (English / Hindi / Gujarati) using Vosk + gTTS
- Avatar support: place `sister.png` in repo root

## Run in Google Colab (recommended)
1. Upload repository to Colab or `git clone`.
2. Upload `app.py`, `requirements.txt`, `run_colab.sh`.
3. Run:
   ```bash
   !bash run_colab.sh
