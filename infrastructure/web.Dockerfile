FROM node:24-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c AS build
WORKDIR /workspace/apps/web
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web ./
COPY scripts/fetch-assets.mjs /workspace/scripts/fetch-assets.mjs
COPY data/assets.lock.json /workspace/data/assets.lock.json
RUN node /workspace/scripts/fetch-assets.mjs
RUN npm run build
FROM node:24-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c
WORKDIR /app
ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000
COPY --from=build --chown=node:node /workspace/apps/web/.next/standalone ./
COPY --from=build --chown=node:node /workspace/apps/web/.next/static ./.next/static
COPY --from=build --chown=node:node /workspace/apps/web/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
