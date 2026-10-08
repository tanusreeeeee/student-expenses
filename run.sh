#!/usr/bin/env bash
cd "$(dirname "$0")"
source .venv/bin/activate && streamlit run app.py --server.address 127.0.0.1
