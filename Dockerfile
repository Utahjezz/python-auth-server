# syntax=docker/dockerfile:1
### BASE IMAGE ###
FROM python:3.10.9-slim as base

RUN mkdir -p /app
RUN useradd --home /app auth_backend && \
    usermod -a -G auth_backend auth_backend && \
    chown -R auth_backend:auth_backend /app

ENV PATH /app/.local/bin:$PATH
ENV PYTHONPATH /app:$PYTHONPATH

USER auth_backend

RUN pip install --user --upgrade pip

COPY --chown=auth_backend:auth_backend requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

### TEST IMAGE ###
FROM base as test

COPY --chown=auth_backend:auth_backend requirements-dev.txt .
RUN pip install --user --no-cache-dir -r requirements-dev.txt

COPY --chown=auth_backend:auth_backend app/ /app
COPY --chown=auth_backend:auth_backend tests/ /tests
COPY --chown=auth_backend:auth_backend pyproject.toml pyproject.toml

ENV PYTHONPATH="${PYTHONPATH}:${APP_HOME}"

ENTRYPOINT ["pytest"]

### RUNTIME IMAGE ###
FROM base as runtime

# Copy local code to the container image.
COPY --chown=auth_backend:auth_backend app/ /app

ENV PYTHONPATH="${PYTHONPATH}:${APP_HOME}"
ENTRYPOINT [ "python", "/app/asgi.py" ]
