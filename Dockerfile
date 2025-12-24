FROM python:3.10-slim

# Install Mono (The C# Compiler)
RUN apt-get update && apt-get install -y mono-mcs && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
