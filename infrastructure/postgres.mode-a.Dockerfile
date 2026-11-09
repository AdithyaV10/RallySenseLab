# Mode A only: fresh generated database/logical restores; never mount existing glibc volumes.
FROM caddy:2.11.9-builder@sha256:3fddbec729442a56b942d4c9eaef1df80893dbf2cf5b86701bfae6aad1408eeb AS fetch
WORKDIR /build
# The official 1.20 binary still uses unsupported Go 1.24.6. Compile the same stable
# source with maintained Go 1.27.3; retain symbols for future govulncheck analysis.
ADD https://github.com/tianon/gosu/archive/refs/tags/1.20.tar.gz /build/gosu.tar.gz
RUN echo '207a2045e890d3ca3326027c5f585733085960b401a49dbc00e3bb628c054cf8  gosu.tar.gz' | sha256sum -c - \
    && tar -xf gosu.tar.gz --strip-components=1 \
    && GOTOOLCHAIN=local CGO_ENABLED=0 go build -mod=readonly -trimpath -ldflags=-w -o /out/gosu .
FROM postgres:17.11-alpine3.24@sha256:3540c0362c809df084ffac0ae69fe794515f9de92692f02178bcdce0ef0302ac
RUN apk upgrade --no-cache

# Same stable official entrypoint helper, rebuilt with the supported Go toolchain.
COPY --from=fetch /out/gosu /usr/local/bin/gosu
RUN gosu nobody true
