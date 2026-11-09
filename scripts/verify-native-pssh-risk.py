"""Bounded diagnostic of the disclosed MOV/PSSH parser defect, in a network-free container.

Uses only a newly generated video. Diagnostic completion does not mean release acceptance.
"""

import json
import subprocess
from pathlib import Path

code = r"""
import json,pathlib,struct,subprocess,tempfile,time
from rallysense.media import probe_video
from rallysense.errors import DomainError
with tempfile.TemporaryDirectory() as folder:
 p=pathlib.Path(folder)/'control.mp4'
 subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=black:s=160x120:r=10','-t','0.5','-c:v','libx264','-an',str(p)],check=True,capture_output=True,timeout=15)
 baseline=probe_video(p)
 raw=p.read_bytes();pos=0;atoms=[]
 while pos<len(raw):
  size,kind=struct.unpack('>I4s',raw[pos:pos+8]);assert size>=8
  atoms.append((kind,raw[pos:pos+size]));pos+=size
 assert atoms[-1][0]==b'moov','Control must have terminal moov so media chunk offsets remain valid'
 # Version-0 PSSH with one data byte; no actual encryption, keys, private data or external references.
 box=struct.pack('>I4s',33,b'pssh')+bytes(4)+bytes.fromhex('edef8ba979d64acea3c827dcd51d21ed')+struct.pack('>I',1)+bytes(1)
 cases=[]
 for count in [32,50000]:
  old=atoms[-1][1];moov=struct.pack('>I',len(old)+len(box)*count)+old[4:]+box*count
  target=pathlib.Path(folder)/f'pssh-{count}.mp4';target.write_bytes(b''.join(a[1] for a in atoms[:-1])+moov)
  started=time.monotonic()
  try:
   result=probe_video(target);outcome={'accepted':True,'codec':result['codec']}
  except DomainError as error:outcome={'accepted':False,'domain_error':error.code,'http_status':error.status}
  cases.append({'pssh_boxes':count,'bytes':target.stat().st_size,'elapsed_s':round(time.monotonic()-started,3),**outcome})
 print(json.dumps({'diagnostic_completed':True,'release_acceptance_passed':False,'advisory':'CVE-2026-107678','control':baseline,'cases':cases,'scope':'Generated unencrypted clip, 512MiB/1CPU/pids64/no network/no mounts; actual bounded application probe path. No private files or database accessed.'}))
"""
run = subprocess.run(
    [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--memory",
        "512m",
        "--cpus",
        "1",
        "--pids-limit",
        "64",
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
Path("docs/evidence/step6_5/native-pssh-risk.json").write_text(
    json.dumps(data, indent=2), encoding="utf-8"
)
print(json.dumps(data))
