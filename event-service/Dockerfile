# 1️⃣ Base image (Python)
FROM python:3.12-slim

# 2️⃣ Set working directory di container
WORKDIR /app

# 3️⃣ Copy requirements & install dependency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4️⃣ Copy seluruh source code
COPY . .

# 5️⃣ Expose port (sesuai service)
EXPOSE 4001

# 6️⃣ Command buat jalanin service
CMD ["python", "run.py"]
