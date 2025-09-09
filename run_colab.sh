#!/bin/bash
apt-get update -y
# ffmpeg already installed in Colab, no need for heavy apt packages

# Install Colab-friendly requirements
pip install -r requirements-colab.txt --upgrade --quiet
