# Dockerfile Patterns

Use this reference when you need a concrete build template.

## Multi-Stage Pattern

```dockerfile
# -- build stage --
FROM node:22.14.0-alpine3.21@sha256:<digest> AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# -- runtime stage --
FROM node:22.14.0-alpine3.21@sha256:<digest> AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
USER node
CMD ["node", "dist/server.js"]
```

## Single-Stage Minimal Example

```dockerfile
FROM python:3.12-slim@sha256:<digest>
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER nobody
CMD ["python", "main.py"]
```
