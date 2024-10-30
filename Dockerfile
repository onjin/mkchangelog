FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update -y && apt-get install -y  git && git config --global --add safe.directory /app

ARG MKCHANGELOG_VERSION
RUN uv tool install mkchangelog==${MKCHANGELOG_VERSION}

WORKDIR /app
ENTRYPOINT [ "uv", "tool", "run", "mkchangelog" ]

