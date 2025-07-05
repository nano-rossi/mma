#!/bin/bash

# Arrancar API en segundo plano
uvicorn src.main.main:app --host 0.0.0.0 --port 8000 &

# Lanzar el bot
python src/main/bot.py