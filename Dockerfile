FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Graphviz using apt-get
RUN apt-get update && \
    apt-get install -y graphviz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["gunicorn", "-b", ":8080", "app:app"]