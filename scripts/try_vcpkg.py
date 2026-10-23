"""Check binary-only vcpkg installation using an isolated, read-only binary cache."""
import datetime
import json
import os
from pathlib import Path
import platform
import subprocess
import time

root = Path(__file__).resolve().parents[1]
deps = root / '.deps'
for name in ('binary-cache', 'downloads', 'registry-cache', 'installed', 'buildtrees', 'packages'):
    (deps / name).mkdir(parents=True, exist_ok=True)
env = dict(os.environ,
    VCPKG_DOWNLOADS=str(deps / 'downloads'),
    VCPKG_REGISTRIES_CACHE=str(deps / 'registry-cache'),
    VCPKG_BINARY_SOURCES=f'clear;files,{deps / "binary-cache"},read',
    VCPKG_DISABLE_METRICS='1')
tool = deps / 'tools/vcpkg/vcpkg'
results = root / 'results'
results.mkdir(exist_ok=True)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
command = [str(tool), 'install', '--only-binarycaching', '--triplet=arm64-osx',
    '--host-triplet=arm64-osx', f'--x-install-root={deps / "installed"}',
    f'--x-buildtrees-root={deps / "buildtrees"}', f'--x-packages-root={deps / "packages"}']

def disk_kib():
    return int(subprocess.check_output(['du', '-sk', str(deps)], text=True).split()[0])

before = disk_kib()
start = time.perf_counter()
with (results / f'{stamp}-vcpkg.log').open('w') as log:
    result = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
elapsed = time.perf_counter() - start
report = dict(timestamp_utc=stamp, system=platform.system(), architecture=platform.machine(),
    command=command, exit_code=result.returncode, elapsed_seconds=round(elapsed, 3),
    deps_before_kib=before, deps_after_kib=disk_kib(), source_builds_allowed=False,
    binary_cache='project-local, read-only; initially empty',
    status='installed' if result.returncode == 0 else 'failed_inspect_log',
    peak_disk_usage='not_measured')
(results / f'{stamp}-vcpkg.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
print((results / f'{stamp}-vcpkg.log').read_text()[-14000:])
raise SystemExit(result.returncode)
