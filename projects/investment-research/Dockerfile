FROM node:24.19.0-bookworm-slim@sha256:a9f5f7c91a432850b2a8a7797adf5eadb6c733ceed61167806cee7ea7fbc29df AS web
WORKDIR /build
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/index.html web/tsconfig.json web/vite.config.ts ./
COPY web/src ./src
RUN npm run build

FROM python:3.12.14-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/api:/app/src
COPY requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt && useradd --uid 10001 --create-home research
COPY api/research_api ./api/research_api
COPY src/research_brief ./src/research_brief
COPY examples/msft-fy2025.json ./examples/msft-fy2025.json
COPY examples/msft-fy2025-passages.json ./examples/msft-fy2025-passages.json
COPY --from=web /build/dist ./web/dist
USER 10001
EXPOSE 8010
CMD ["uvicorn", "research_api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8010", "--no-access-log"]
