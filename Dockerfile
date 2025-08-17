FROM python:3.9-slim

# Installiere Systemabhängigkeiten für OpenCV und andere Bibliotheken
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere den gesamten Projektinhalt
COPY . .

# Installiere die Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Exponiere den Port, auf dem die App läuft
EXPOSE 5000

# Starte die Anwendung
CMD ["python", "app.py"]