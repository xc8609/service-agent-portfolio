FROM node:24.19.0-bookworm-slim@sha256:a9f5f7c91a432850b2a8a7797adf5eadb6c733ceed61167806cee7ea7fbc29df AS web
WORKDIR /build
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/index.html apps/web/tsconfig.json apps/web/vite.config.ts ./
COPY apps/web/src ./src
RUN npm run build

FROM python:3.12.14-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/services/api
COPY services/api/requirements.lock /app/services/api/requirements.lock
RUN pip install --no-cache-dir -r services/api/requirements.lock && useradd --uid 10001 --create-home demo
COPY services/api/bank_api /app/services/api/bank_api
COPY services/api/migrations /app/services/api/migrations
COPY projects/bank-service-assist/specs/contracts/agent-tools.json /app/projects/bank-service-assist/specs/contracts/agent-tools.json
COPY projects/bank-service-assist/specs/DEV-03/investigation-input.schema.json /app/projects/bank-service-assist/specs/DEV-03/investigation-input.schema.json
COPY --from=web /build/dist /app/apps/web/dist
USER 10001
EXPOSE 8000
CMD ["uvicorn", "bank_api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
