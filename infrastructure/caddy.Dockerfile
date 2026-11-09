# Official maintained Caddy release/toolchain; patch only the affected supported Go module.
FROM caddy:2.11.9-builder@sha256:3fddbec729442a56b942d4c9eaef1df80893dbf2cf5b86701bfae6aad1408eeb AS build
RUN xcaddy build v2.11.9 \
    --replace golang.org/x/net=golang.org/x/net@v0.62.0 \
    --output /out/caddy
FROM caddy:2.11.9-alpine@sha256:78bd35025c7ba85961dd149ae670315129954e77abe2383ac47c89106b35ade9
COPY --from=build /out/caddy /usr/bin/caddy
