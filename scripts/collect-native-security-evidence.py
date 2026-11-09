"""Record real native build features, hashes and scientific runtime; no private records."""

import json
import subprocess
from pathlib import Path

code = r"""
import ctypes.util,hashlib,importlib.util,json,os,pathlib,shutil,subprocess
from rallysense.provenance import execution_environment
from rallysense.media import native_environment
def run(*args):
 r=subprocess.run(args,capture_output=True,text=True,check=True)
 return r.stdout.strip()
out={'runtime':execution_environment(),'uid':os.getuid(),'uv_present':shutil.which('uv') is not None,
 'native_inherited_environment_keys':sorted(native_environment()),
 'top_level_modules':{p:(s.origin if (s:=importlib.util.find_spec(p)) else None) for p in ['msgpack','setuptools','urllib3']},
 'libxml2':ctypes.util.find_library('xml2'),
 'binaries':{p:hashlib.sha256(pathlib.Path('/usr/local/bin',p).read_bytes()).hexdigest() for p in ['ffmpeg','ffprobe']},
 'native_versions':run('ffmpeg','-version'),
 'demuxers':run('ffprobe','-hide_banner','-demuxers'),
 'decoders':run('ffprobe','-hide_banner','-decoders'),
 'protocols':run('ffprobe','-hide_banner','-protocols'),
 'muxers':run('ffmpeg','-hide_banner','-muxers'),
 'filters':run('ffmpeg','-hide_banner','-filters'),
 'shared_libraries':run('ldd','/usr/local/bin/ffprobe'),
 'runtime_libraries':run('dpkg-query','-W','libx264-164','libvpx9')}
assert out['uid']!=0 and out['libxml2'] is None and not out['uv_present']
assert all(out['top_level_modules'][p] is None for p in out['top_level_modules'])
assert not any(p in out['protocols'].splitlines() for p in ['  http','  https','  tcp','  udp'])
print(json.dumps(out))
"""
run = subprocess.run(
    [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "-i",
        "--entrypoint",
        "python",
        "rallysense-api:rc-step6_5",
        "-",
    ],
    input=code,
    text=True,
    capture_output=True,
    encoding="utf-8",
    check=True,
    timeout=90,
)
data = json.loads(run.stdout)
Path("docs/evidence/step6_5/native-runtime.json").write_text(
    json.dumps(data, indent=2), encoding="utf-8"
)
sbom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.6",
    "version": 1,
    "components": [
        {
            "type": "application",
            "name": "FFmpeg",
            "version": "9.0.2",
            "bom-ref": "ffmpeg-9.0.2-limited-rallysense",
            "purl": "pkg:generic/ffmpeg@9.0.2",
            "licenses": [{"license": {"id": "GPL-2.0-or-later"}}],
            "externalReferences": [
                {
                    "type": "distribution",
                    "url": "https://ffmpeg.org/releases/ffmpeg-9.0.2.tar.xz",
                }
            ],
            "hashes": [
                {
                    "alg": "SHA-256",
                    "content": "8c3850283eb25fa026482078a04051e0be17347b09ef81a0849bec15a96e002e",
                }
            ],
            "properties": [
                {
                    "name": "rallysense:coverage",
                    "value": "Source component inventory; custom static FFmpeg is not covered by Debian package matching. See native-runtime.json, vendor advisory matrix and Dockerfile for binary hashes/features; this SBOM does not suppress findings.",
                }
            ],
        }
    ],
}
Path("infrastructure/media-components.cdx.json").write_text(
    json.dumps(sbom, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {
            "native_features_verified": True,
            "libxml2_absent": True,
            "network_protocols_absent": True,
            "binary_hashes": data["binaries"],
            "runtime": data["runtime"],
        }
    )
)
