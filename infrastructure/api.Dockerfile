# Supported stable glibc base; numerical dependencies remain frozen in uv.lock.
FROM python:3.13-slim-trixie@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90 AS base
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

FROM base AS dependencies
COPY --from=ghcr.io/astral-sh/uv:0.12.23@sha256:61d393e44e249f2e4b526b6c7ddcecce245946826e608e11c93ad4f5bba55b21 /uv /usr/local/bin/uv
WORKDIR /app
COPY apps/api/pyproject.toml apps/api/uv.lock ./
COPY apps/api/src ./src
RUN uv sync --frozen --no-dev

FROM base AS media-build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config nasm ca-certificates curl xz-utils libx264-dev libvpx-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
# Official stable release; SHA-256 is tied to the verified upstream release signature.
ADD https://ffmpeg.org/releases/ffmpeg-9.0.2.tar.xz /build/ffmpeg.tar.xz
RUN echo '8c3850283eb25fa026482078a04051e0be17347b09ef81a0849bec15a96e002e  ffmpeg.tar.xz' | sha256sum -c - \
    && tar -xf ffmpeg.tar.xz --strip-components=1 \
    && ./configure --prefix=/opt/media --disable-autodetect --disable-shared --enable-static \
       --disable-doc --disable-debug --disable-network --disable-everything \
       --enable-ffmpeg --enable-ffprobe --disable-ffplay --enable-gpl \
       --enable-libx264 --enable-libvpx --enable-pthreads \
       --enable-protocol=file,pipe,crypto \
       --enable-demuxer=mov,matroska,rawvideo \
       --enable-muxer=mp4,webm \
       --enable-decoder=h264,vp8,vp9,rawvideo,wrapped_avframe \
       --enable-encoder=libx264,libvpx_vp8,libvpx_vp9 \
       --enable-parser=h264,vp8,vp9 \
       --enable-bsf=h264_mp4toannexb,extract_extradata \
       --enable-filter=color,format,scale,null,anull \
       --enable-indev=lavfi \
    && make -j4 && make install \
    && mkdir -p /opt/media/share/licenses \
    && cp COPYING* LICENSE.md /opt/media/share/licenses/

FROM base AS runtime-base
WORKDIR /app
COPY --from=dependencies /app/.venv ./.venv
# Frozen manifest lookup intentionally retains this exact lock path.
COPY apps/api/pyproject.toml apps/api/uv.lock ./
COPY apps/api/src ./src
COPY apps/api/alembic.ini ./
COPY apps/api/migrations ./migrations
ENV PATH="/app/.venv/bin:/usr/local/bin:/usr/bin:/bin" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN /usr/sbin/useradd --create-home lab && mkdir -p /data/storage && chown lab:lab /data /data/storage
USER lab

# Viewing precomputed fixtures needs no native media executables or libraries.
FROM runtime-base AS readonly
USER root
# Mode A never installs packages. Remove pip's executable/vendor code, its SBOM,
# and the ensurepip bootstrap wheel together, rather than suppressing its findings.
RUN rm -rf /usr/local/lib/python3.13/site-packages/pip \
           /usr/local/lib/python3.13/site-packages/pip-*.dist-info \
           /usr/local/lib/python3.13/ensurepip \
    && rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.13
USER lab

# Full workspace keeps native features required by supported MP4/WebM workflows.
FROM runtime-base AS workspace
USER root
RUN apt-get update && apt-get install -y --no-install-recommends libx264-164 libvpx9 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=media-build /opt/media/bin/ffmpeg /opt/media/bin/ffprobe /usr/local/bin/
COPY --from=media-build /opt/media/share/licenses /usr/local/share/licenses/ffmpeg
USER lab
