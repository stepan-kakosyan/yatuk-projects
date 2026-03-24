FROM python:3.10-slim

# System dependencies:
#   - gcc, pkg-config, default-libmysqlclient-dev  → mysqlclient build
#   - libcairo2, libpango-1.0-0, libpangocairo-1.0-0,
#     libgdk-pixbuf2.0-0, libffi-dev, shared-mime-info → WeasyPrint
#   - libssl-dev → cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        pkg-config \
        default-libmysqlclient-dev \
        libssl-dev \
        libcairo2 \
        libcairo2-dev \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        libffi-dev \
        shared-mime-info \
        ghostscript \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared apps first (used by all projects via sys.path injection in settings)
COPY shared_apps/ ./shared_apps/

# Copy each Django project
COPY yatuk/     ./yatuk/
COPY yatukplay/ ./yatukplay/
COPY yatukpoem/ ./yatukpoem/
COPY yatukcanvas/ ./yatukcanvas/
COPY cms/       ./cms/


# Entrypoint script (runs collectstatic then gunicorn bound to 0.0.0.0)
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Gunicorn runs on this port inside every container
EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
