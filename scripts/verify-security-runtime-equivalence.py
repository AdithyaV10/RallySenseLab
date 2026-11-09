"""Compare deterministic generated scientific outputs in rollback and candidate containers."""

import argparse
import json
import subprocess
from pathlib import Path

code = r"""
import hashlib,json
from rallysense.provenance import execution_environment
from rallysense.research_fixture import fixture_inputs
from rallysense.signals import normalize_csv,detect_gyro
from rallysense.schemas import SensorMapping,DetectorConfig
from rallysense.research_schemas import VideoConfig,Corruption
from rallysense.research import corrupt,detect_imu,detect_video,associate,evaluate
from rallysense.errors import DomainError
raw,frames=fixture_inputs()
table,_=normalize_csv(raw,SensorMapping())
conditions=[{}, {'dropout_fraction':.2}, {'gyro_noise_sd':.3}, {'acceleration_noise_sd':1},
 {'timestamp_jitter_fraction':.4}, {'imu_gap_start_s':1.5,'imu_gap_duration_s':1},
 {'occlusion_start_s':1.5,'occlusion_duration_s':1}, {'sync_error_us':1000000},
 {'occlusion_duration_s':8}, {'gyro_noise_sd':.15,'dropout_fraction':.1}, {'timestamp_jitter_fraction':.2,'gyro_noise_sd':.1}]
outputs=[]
for knobs in conditions:
 t,f,summary=corrupt(table,frames,Corruption(seed=42,**knobs))
 result={'condition':knobs,'summary':summary}
 for name,fn in [('legacy',lambda:detect_gyro(t,DetectorConfig())),('imu',lambda:detect_imu(t,DetectorConfig(),0)),('video',lambda:detect_video(f,VideoConfig()))]:
  try:result[name]=fn()
  except DomainError as e:result[name]={'error':e.code}
 if 'events' in result['imu'] and 'events' in result['video']:
  try:
   result['fusion']=associate(result['imu'],result['video'],150000)
   result['score']=evaluate(result['fusion']['events'],[{'t_session_us':2000000},{'t_session_us':5000000}],150000,8000000)
  except DomainError as e:result['fusion']={'error':e.code}
 outputs.append(result)
blob=json.dumps(outputs,sort_keys=True,allow_nan=False).encode()
print(json.dumps({'runtime':execution_environment()['runtime'],'dependency_lock_sha256':execution_environment()['dependency_lock_sha256'],'conditions':len(conditions),'deterministic_output_sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob),'scope':'Generated analytical software cases only; not tennis accuracy'}))
"""
parser = argparse.ArgumentParser()
parser.add_argument('--stage', choices=['step6_5', 'step6_6'], default='step6_5')
stage = parser.parse_args().stage
results = {}
for name, image in [
    ("rollback", "rallysense-api-readonly:release-step6_5-rc1" if stage == 'step6_6' else "rallysense-api:release-ac75d818"),
    ("candidate", "rallysense-api-readonly:rc-step6_6" if stage == 'step6_6' else "rallysense-api:rc-step6_5"),
]:
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
            image,
            "-",
        ],
        input=code,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=90,
    )
    results[name] = json.loads(run.stdout)
assert (
    results["rollback"]["deterministic_output_sha256"]
    == results["candidate"]["deterministic_output_sha256"]
)
assert (
    results["rollback"]["dependency_lock_sha256"]
    == results["candidate"]["dependency_lock_sha256"]
)
Path(f"docs/evidence/{stage}/runtime-equivalence.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print(json.dumps({"equivalent": True, "results": results}))
