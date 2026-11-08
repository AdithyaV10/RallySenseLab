"""Real loopback streaming boundary/abort/concurrency verification; synthetic fixtures only."""

import asyncio
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:3000"
HEADERS = {"x-lab-client": "rallysense"}


class Journal(list):
    def append(self, item):
        super().append(item)
        Path("docs/evidence/step5_5/upload-boundaries-progress.json").write_text(
            json.dumps({"completed_cases": self, "complete": False}, indent=2),
            encoding="utf-8",
        )


results = Journal()
sessions = []


def command(*args):
    return subprocess.check_output(args, text=True, encoding="utf-8").strip()


def memory():
    # Kernel process high-water marks, not a guessed multiplier or external benchmark.
    code = """import json,pathlib
out=[]
for p in pathlib.Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   cmd=(p/'cmdline').read_bytes().split(b'\\0')
   if p.name=='1' or any(a.endswith(b'/uvicorn') for a in cmd):
    status=dict(line.split(':',1) for line in (p/'status').read_text().splitlines() if ':' in line)
    out.append({k:status.get(k,'').strip() for k in ['Name','VmRSS','VmHWM']})
  except OSError: pass
print(json.dumps(out))"""
    return {
        "web_process": command(
            "docker",
            "exec",
            "rallysense-web-1",
            "sh",
            "-c",
            "cat /proc/1/status | sed -n '/^Name:/p;/^VmRSS:/p;/^VmHWM:/p'",
        ),
        "api_processes": json.loads(
            command("docker", "exec", "rallysense-api-1", "python", "-c", code)
        ),
    }


def verify_hash(job, expected):
    code = """import hashlib,json,sys
from sqlalchemy.orm import Session
from rallysense import models as m
from rallysense.db import engine
from rallysense.storage import path_for
with Session(engine) as db:
 job=db.get(m.ProcessingJob,sys.argv[1])
 source=db.get(m.SensorRecording if job.kind=='normalize' else m.VideoAsset,job.target_id)
 aid=source.raw_artifact_id if job.kind=='normalize' else source.artifact_id
 a=db.get(m.Artifact,aid)
 with path_for(db,aid,job.session_id).open('rb') as f: actual=hashlib.file_digest(f,'sha256').hexdigest()
 print(json.dumps({'bytes':a.bytes,'stored_sha256':a.sha256,'actual_sha256':actual}))"""
    actual = json.loads(
        command("docker", "exec", "rallysense-api-1", "python", "-c", code, job["id"])
    )
    assert actual["actual_sha256"] == actual["stored_sha256"] == expected
    return actual


def wait_job(client, job):
    for _ in range(300):
        state = client.get(BASE + "/api/v1/jobs/" + job["id"]).json()
        if state["state"] in {"failed", "cancelled", "succeeded"}:
            assert state["state"] == "succeeded", state
            return
        time.sleep(0.2)
    raise AssertionError("Fixture processing timed out")


def parts(path, kind):
    yield (
        b'--step55\r\nContent-Disposition: form-data; name="file"; filename="fixture.'
        + (b"csv" if kind == "csv" else b"mp4")
        + b'"\r\nContent-Type: application/octet-stream\r\n\r\n'
    )
    with path.open("rb") as stream:
        while chunk := stream.read(64 * 1024):
            yield chunk
    field = b"mapping" if kind == "csv" else b"metadata"
    yield (
        b'\r\n--step55\r\nContent-Disposition: form-data; name="'
        + field
        + b'"\r\n\r\n{"provenance":"synthetic"}\r\n--step55--\r\n'
    )


async def concurrent_abort_checks(sid):
    route = f"/api/v1/sessions/{sid}/videos"
    prefix = b'--step55\r\nContent-Disposition: form-data; name="file"; filename="partial.mp4"\r\n\r\n'

    async def opening():
        reader, writer = await asyncio.open_connection("127.0.0.1", 3000)
        writer.write(
            (
                f"POST {route} HTTP/1.1\r\nHost: 127.0.0.1:3000\r\nx-lab-client: rallysense\r\nContent-Type: multipart/form-data; boundary=step55\r\nTransfer-Encoding: chunked\r\n\r\n"
            ).encode()
        )
        writer.write(f"{len(prefix):x}\r\n".encode() + prefix + b"\r\n")
        await writer.drain()
        return reader, writer

    first, second = await opening(), await opening()
    try:
        await asyncio.sleep(1)
        async with httpx.AsyncClient(timeout=10) as client:
            rejected = await client.post(
                BASE + route,
                headers=HEADERS,
                files={"file": ("extra.mp4", b"not video")},
            )
            assert rejected.status_code == 429, rejected.text
        results.append(
            {"case": "third_inflight_upload", "status": 429, "active_limit": 2}
        )
    finally:
        for _, writer in [first, second]:
            writer.close()
            await writer.wait_closed()
    await asyncio.sleep(1)
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(BASE + f"/api/v1/sessions/{sid}")
        detail = response.json()
        assert not detail["videos"], detail["videos"]
        results.append({"case": "two_aborted_uploads", "published_videos": 0})
    reader, writer = await opening()
    started = time.monotonic()
    try:
        status_line = await asyncio.wait_for(reader.readline(), timeout=40)
        assert b" 408 " in status_line, status_line
        results.append(
            {
                "case": "idle_upload_timeout",
                "status": 408,
                "elapsed_s": round(time.monotonic() - started, 2),
            }
        )
    finally:
        writer.close()
        await writer.wait_closed()
    async with httpx.AsyncClient(timeout=40) as client:
        payload = Path("storage/step5-small.mp4").read_bytes()
        responses = await asyncio.gather(
            *[
                client.post(
                    BASE + route,
                    headers=HEADERS,
                    files={"file": ("synthetic.mp4", payload, "video/mp4")},
                    data={"metadata": '{"provenance":"synthetic"}'},
                )
                for _ in range(2)
            ]
        )
        assert [r.status_code for r in responses] == [202, 202]
        for response in responses:
            job = response.json()
            for _ in range(100):
                state = (await client.get(BASE + "/api/v1/jobs/" + job["id"])).json()[
                    "state"
                ]
                if state == "succeeded":
                    break
                assert state not in {"failed", "cancelled"}
                await asyncio.sleep(0.2)
            else:
                raise AssertionError("Concurrent valid fixture job timed out")
            verify_hash(job, hashlib.sha256(payload).hexdigest())
        results.append(
            {
                "case": "two_concurrent_valid_uploads",
                "statuses": [202, 202],
                "worker_results": ["succeeded", "succeeded"],
                "hashes_verified": True,
            }
        )


before_memory = memory()
with (
    tempfile.TemporaryDirectory(prefix="step55-upload-", dir="storage") as temp,
    httpx.Client(timeout=180) as client,
):
    directory = Path(temp)
    try:
        response = client.post(
            BASE + "/api/v1/sessions",
            headers=HEADERS,
            json={"title": "Disposable upload boundaries", "dataset_kind": "synthetic"},
        )
        assert response.status_code == 201
        sid = response.json()["id"]
        sessions.append(sid)
        csv = directory / "near-limit.csv"
        header = (
            b"timestamp_s,ax_m_s2,ay_m_s2,az_m_s2,gx_rad_s,gy_rad_s,gz_rad_s,padding\n"
        )
        prefixes = [f"{i / 1000:.3f},0,0,9.80665,0,0,0,".encode() for i in range(1001)]
        pad, extra = divmod(
            50 * 1024 * 1024 - len(header) - sum(map(len, prefixes)) - len(prefixes),
            len(prefixes),
        )
        with csv.open("wb") as stream:
            stream.write(header)
            for i, prefix in enumerate(prefixes):
                stream.write(prefix + b"x" * (pad + (i < extra)) + b"\n")
        video = directory / "near-limit.mp4"
        source = Path("storage/step5-small.mp4")
        with video.open("wb") as stream:
            stream.write(source.read_bytes())
            padding = 500 * 1024 * 1024 - stream.tell()
            stream.write(padding.to_bytes(4, "big") + b"free")
            stream.seek(500 * 1024 * 1024 - 1)
            stream.write(b"\0")
        for kind, path in [("csv", csv), ("video", video)]:
            route = f"/api/v1/sessions/{sid}/" + (
                "sensor-imports" if kind == "csv" else "videos"
            )
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            started = time.monotonic()
            # A generator deliberately omits Content-Length and exercises chunked ingress.
            response = client.post(
                BASE + route,
                headers={
                    **HEADERS,
                    "content-type": "multipart/form-data; boundary=step55",
                },
                content=parts(path, kind),
            )
            assert response.status_code == 202, (
                kind,
                response.status_code,
                response.text,
            )
            job = response.json()
            wait_job(client, job)
            results.append(
                {
                    "case": f"{kind}_exact_file_limit_chunked",
                    "status": response.status_code,
                    "elapsed_s": round(time.monotonic() - started, 3),
                    **verify_hash(job, digest),
                }
            )
            with path.open("ab") as stream:
                stream.write(b"x")
            response = client.post(
                BASE + route,
                headers={
                    **HEADERS,
                    "content-type": "multipart/form-data; boundary=step55",
                },
                content=parts(path, kind),
            )
            assert response.status_code == 413, (
                kind,
                response.status_code,
                response.text,
            )
            results.append({"case": f"{kind}_file_limit_plus_one", "status": 413})
        route = f"/api/v1/sessions/{sid}/sensor-imports"
        with csv.open("ab") as stream:
            stream.write(b"x" * (2 * 1024 * 1024))
        response = client.post(
            BASE + route,
            headers={**HEADERS, "content-type": "multipart/form-data; boundary=step55"},
            content=parts(csv, "csv"),
        )
        assert response.status_code == 413, (response.status_code, response.text)
        results.append({"case": "chunked_total_body_over_51_mib", "status": 413})
        for name, headers, content, expected in [
            (
                "multipart_request_content_length_over_limit",
                {**HEADERS, "content-length": str(51 * 1024 * 1024 + 1)},
                b"",
                413,
            ),
            (
                "malformed_multipart",
                {**HEADERS, "content-type": "multipart/form-data; boundary=missing"},
                b"broken",
                400,
            ),
            (
                "foreign_origin",
                {**HEADERS, "origin": "https://untrusted.invalid"},
                b"",
                403,
            ),
            ("foreign_host", {**HEADERS, "host": "untrusted.invalid"}, b"", 403),
            ("missing_client_guard", {}, b"", 403),
        ]:
            # Raw HTTP permits an early rejection without transmitting a declared oversized body.
            if name == "multipart_request_content_length_over_limit":
                import http.client

                connection = http.client.HTTPConnection("127.0.0.1", 3000, timeout=10)
                connection.putrequest("POST", route)
                for key, value in headers.items():
                    connection.putheader(key, value)
                connection.endheaders()
                result = connection.getresponse()
                status = result.status
                result.read()
                connection.close()
            else:
                response = client.post(BASE + route, headers=headers, content=content)
                status = response.status_code
            assert status == expected, (name, status)
            results.append({"case": name, "status": status})
        empty = client.post(
            BASE + "/api/v1/sessions",
            headers=HEADERS,
            json={"title": "Disposable aborted streams", "dataset_kind": "synthetic"},
        ).json()["id"]
        sessions.append(empty)
        asyncio.run(concurrent_abort_checks(empty))
    finally:
        for sid in sessions:
            client.delete(BASE + "/api/v1/sessions/" + sid, headers=HEADERS)
after_memory = memory()
result = {
    "scope": "Synthetic loopback tests; exact 50/500 MiB file bounds, chunked bodies, real workers, stored byte hashes, abort and concurrency",
    "cases": results,
    "memory_before": before_memory,
    "memory_after": after_memory,
    "memory_note": "VmHWM is the kernel-observed process lifetime peak RSS, including earlier checks; not isolated upload-only RSS or a production capacity benchmark.",
}
Path("docs/evidence/step5_5/upload-boundaries-results.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
Path("docs/evidence/step5_5/upload-boundaries-progress.json").write_text(
    json.dumps({"completed_cases": results, "complete": True}, indent=2), encoding="utf-8"
)
print(json.dumps(result, indent=2))
