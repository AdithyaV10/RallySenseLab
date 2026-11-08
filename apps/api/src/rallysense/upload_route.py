"""Restrict multipart parser resources before FastAPI resolves upload dependencies."""
from fastapi.routing import APIRoute


class BoundedUploadRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def bounded(request):
            if request.method == "POST" and request.url.path.endswith(("/videos", "/sensor-imports")):
                # Parser spools files to disk above 1 MiB. One file + one metadata
                # field prevents a bounded-byte request from exhausting file handles.
                async with request.form(max_files=1, max_fields=1, max_part_size=64 * 1024):
                    return await handler(request)
            return await handler(request)

        return bounded
