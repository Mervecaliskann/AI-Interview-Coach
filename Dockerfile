# 1. Temel İmaj: Python'un hafif sürümünü kullan
FROM python:3.10-slim

# 2. Çalışma klasörünü ayarla
WORKDIR /app

# 3. Önce kütüphane listesini kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kodların geri kalanını kopyala
COPY . .

# 5. Portu dışarı aç
EXPOSE 8501

# 6. Uygulamayı başlat
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]