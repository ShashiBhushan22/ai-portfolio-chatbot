#!/bin/bash
# Run the AI Chatbot Server

cd /home/bhushan-arc/AI_Engineer/ai-portfolio-chatbot/backend
/home/bhushan-arc/AI_Engineer/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
