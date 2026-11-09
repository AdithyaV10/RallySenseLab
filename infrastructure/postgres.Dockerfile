# Retain PostgreSQL major version, glibc distro, entrypoint, data paths and locale behavior.
FROM caddy:2.11.9-builder@sha256:3fddbec729442a56b942d4c9eaef1df80893dbf2cf5b86701bfae6aad1408eeb AS fetch
WORKDIR /build
# The official 1.20 binary still uses unsupported Go 1.24.6. Compile the same stable
# source with maintained Go 1.27.3; retain symbols for future govulncheck analysis.
ADD https://github.com/tianon/gosu/archive/refs/tags/1.20.tar.gz /build/gosu.tar.gz
RUN echo '207a2045e890d3ca3326027c5f585733085960b401a49dbc00e3bb628c054cf8  gosu.tar.gz' | sha256sum -c - \
    && tar -xf gosu.tar.gz --strip-components=1 \
    && GOTOOLCHAIN=local CGO_ENABLED=0 go build -mod=readonly -trimpath -ldflags=-w -o /out/gosu .
FROM postgres:17-trixie@sha256:ff87138949ad9a46f32ff23bd6852b52ce024a13dffe9b4087be98292cdd3b4f
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
COPY --from=fetch /out/gosu /usr/local/bin/gosu
RUN gosu nobody true
