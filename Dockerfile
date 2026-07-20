FROM python:3.13-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /usr/src/app
COPY . .
VOLUME /usr/src/app/data
EXPOSE 8080
CMD ["uv", "run", "serve.py"]
