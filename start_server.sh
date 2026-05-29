#!/bin/bash
set -a
source ~/.hermes/.env
set +a
cd /root/expertise-transfer-engine
exec uvicorn backend.main:app --host 127.0.0.1 --port 8010
