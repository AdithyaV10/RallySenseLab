FROM node:24-bookworm-slim@sha256:01d566e8d94d8c619591d78652babfccd3c6992a3dffa9ed5ab39e11cf6c70e9 AS build
WORKDIR /workspace/apps/web
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web ./
COPY scripts/fetch-assets.mjs /workspace/scripts/fetch-assets.mjs
COPY data/assets.lock.json /workspace/data/assets.lock.json
RUN node /workspace/scripts/fetch-assets.mjs
RUN npm run build
# Same maintained Node ABI on stable glibc; trixie supplies patched system zlib.
FROM node:24-trixie-slim@sha256:0820eaa85e07d0490446dd01d14707e17e6108a36988cf374899cd057eb3812d
RUN apt-get update && apt-get upgrade -y \
    && rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack /opt/yarn* \
    && rm -f /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack /usr/local/bin/yarn /usr/local/bin/yarnpkg \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000
COPY --from=build --chown=node:node /workspace/apps/web/.next/standalone ./
COPY --from=build --chown=node:node /workspace/apps/web/.next/static ./.next/static
COPY --from=build --chown=node:node /workspace/apps/web/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
