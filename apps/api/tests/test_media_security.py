"""Native-parser security boundaries, with real child processes and supported media."""

import json
import os
import shutil
import subprocess
import sys

import pytest

from rallysense.errors import DomainError
from rallysense.media import probe_video


def test_native_probe_child_does_not_receive_application_secrets(tmp_path, monkeypatch):
    # An observable replacement child proves the environment actually passed to exec.
    executable = tmp_path / "ffprobe"
    environment = tmp_path / "child-environment.json"
    executable.write_text(
        f"#!{sys.executable}\nimport os,json\n"
        f"open({str(environment)!r},'w').write(json.dumps(dict(os.environ)))\n"
        "print(json.dumps({'streams':[{'codec_type':'video','codec_name':'h264','width':160,'height':120}],"
        "'format':{'duration':'1','format_name':'mov,mp4,m4a,3gp,3g2,mj2'}}))\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    for key in ["DATABASE_URL", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD", "AWS_SECRET_ACCESS_KEY"]:
        monkeypatch.setenv(key, "must-not-reach-native-parser")
    assert probe_video(tmp_path / "source.mp4")["codec"] == "h264"
    child = json.loads(environment.read_text())
    assert "must-not-reach-native-parser" not in json.dumps(child)


def test_native_probe_rejects_an_external_playlist(tmp_path):
    playlist = tmp_path / "disguised.mp4"
    # No request may be sent to an external protocol or HLS demuxer.
    playlist.write_text("#EXTM3U\n#EXT-X-TARGETDURATION:1\n#EXTINF:1,\nhttp://127.0.0.1:9/forbidden.ts\n")
    with pytest.raises(DomainError) as error:
        probe_video(playlist)
    assert error.value.status == 415


def test_supported_vp9_remains_probeable(tmp_path):
    assert shutil.which("ffmpeg"), "Required container runtime tool is absent"
    video = tmp_path / "vp9.webm"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=160x120:r=10",
            "-t",
            "0.5",
            "-c:v",
            "libvpx-vp9",
            "-an",
            str(video),
        ],
        check=True,
        capture_output=True,
        timeout=30,
    )
    assert probe_video(video)["codec"] == "vp9"
