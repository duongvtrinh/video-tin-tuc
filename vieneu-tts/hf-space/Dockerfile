FROM python:3.12-slim

WORKDIR /app

# soundfile cần libsndfile của hệ thống
RUN apt-get update \
    && apt-get install -y --no-install-recommends libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Tải sẵn model VieNeu-TTS v3 Nano vào image để container khởi động nhanh,
# lần gọi đầu không phải chờ download.
RUN python -c "from vieneu import Vieneu; Vieneu(mode='v3nano'); print('model cached OK')"

EXPOSE 7860

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
