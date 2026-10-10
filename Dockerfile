FROM node:26-slim@sha256:930557a230abacbc3f4fd9b8648abf8f4bee1e17cb72195dcdfb2f709bc85b33 AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --ignore-scripts
COPY frontend .
RUN npm run build

FROM python:3.12-slim@sha256:05cda9777409a9c3ffddd94a4c476b79f0769a0b4857f0c7ed9226b6800b0d6f
WORKDIR /app

# gosu drops root privileges after the entrypoint chowns the /app/data
# mount, so existing installs whose data dir was created by the old,
# always-root image still work after upgrading.
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY VERSION .
COPY --from=frontend-build /frontend/dist ./frontend/dist
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

VOLUME ["/app/data"]
EXPOSE 8000

# Defined here rather than in docker-compose.yml so it also applies to
# `docker run` and other orchestrators — Compose inherits an image's
# HEALTHCHECK automatically, so it doesn't need its own duplicate section.
# Uses stdlib urllib instead of curl to avoid an extra apt package.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=3)" || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
