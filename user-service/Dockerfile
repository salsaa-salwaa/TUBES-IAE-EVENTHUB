FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 3001 as defined in config.py
EXPOSE 3001

CMD ["python", "app.py"]
