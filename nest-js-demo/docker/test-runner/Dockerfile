# syntax=docker/dockerfile:1

FROM node:20-bookworm AS test-runner

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends wget \
  && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ENV NODE_ENV=test
ENV DATABASE_PATH=/tmp/app.sqlite

# Default command; overridden by K8s Job spec
CMD ["npm", "test"]
