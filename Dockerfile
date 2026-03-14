FROM python:3.12-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/sports-betting-mcp /usr/local/bin/sports-betting-mcp

USER nobody

ENTRYPOINT ["sports-betting-mcp"]
