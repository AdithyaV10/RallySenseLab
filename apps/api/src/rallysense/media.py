import json
import subprocess
from pathlib import Path
from .errors import DomainError


def probe_video(path: Path) -> dict:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-protocol_whitelist",
                "file,crypto",
                "-show_entries",
                "stream=codec_type,codec_name,width,height,time_base,start_time,avg_frame_rate:stream_side_data=rotation:format=duration,format_name",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            timeout=20,
            check=True,
        )
        if len(result.stdout) > 1_000_000:
            raise DomainError("Video metadata exceeds limit", "RESOURCE_LIMIT")
        probe = json.loads(result.stdout)
        stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
        codec = stream["codec_name"]
        duration = float(probe["format"]["duration"])
        width, height = int(stream["width"]), int(stream["height"])
        formats = probe["format"]["format_name"]
        if codec not in ["h264", "vp8", "vp9"] or not any(f in formats for f in ["mp4", "webm", "matroska"]):
            raise DomainError("Use MP4 H.264 or WebM VP8/VP9", "UNSUPPORTED_MEDIA", 415)
        if not (0 < duration <= 600) or width * height > 1920 * 1080:
            raise DomainError("Video must be <=10 minutes and <=1920×1080 pixels", "RESOURCE_LIMIT", 413)
        return {
            "duration_us": round(duration * 1_000_000),
            "width": width,
            "height": height,
            "codec": codec,
            "format": formats,
            "time_base": stream.get("time_base"),
            "start_time": stream.get("start_time", "0"),
            "frame_rate": stream.get("avg_frame_rate"),
            "rotation": next(
                (x.get("rotation", 0) for x in stream.get("side_data_list", []) if "rotation" in x), 0
            ),
            "media_type": "video/mp4" if "mp4" in formats else "video/webm",
        }
    except FileNotFoundError as exc:
        raise DomainError(
            "FFprobe unavailable; use the provided API container", "DEPENDENCY_UNAVAILABLE", 503
        ) from exc
    except (subprocess.SubprocessError, ValueError, KeyError, StopIteration) as exc:
        raise DomainError("File could not be decoded as a supported video", "UNSUPPORTED_MEDIA", 415) from exc
