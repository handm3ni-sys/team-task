# Image dasar Python versi ringan
FROM python:3.12-slim

# Folder kerja di dalam kontainer
WORKDIR /app

# Salin kode backend ke dalam image
COPY app.py .

# Folder data, nanti di-mount ke Named Volume team-task-data
ENV DATA_DIR=/var/lib/backend_data
RUN mkdir -p /var/lib/backend_data

# Backend mendengarkan di port 5000
EXPOSE 5000

# Jalankan server saat kontainer start
CMD ["python", "app.py"]