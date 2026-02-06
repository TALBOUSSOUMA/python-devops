# -------- Stage 1 : Builder --------
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt


# -------- Stage 2 : Runtime --------
FROM python:3.11-alpine

WORKDIR /app

# Créer utilisateur non-root
RUN adduser -D appuser

# Copier dépendances du builder
COPY --from=builder /root/.local /home/appuser/.local

# Copier code source
COPY app ./app

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

EXPOSE 5000

CMD ["python", "app/main.py"]
