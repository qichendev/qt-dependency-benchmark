"""Attempt binary-only acquisition; retain local logs and timing, including failures."""
import datetime
import json
import os
from pathlib import Path
import platform
import subprocess
import time

root = Path(__file__).resolve().parents[1]
env = dict(os.environ, CONAN_HOME=str(root / '.deps/conan'))
conan = root / '.deps/tools/conan/bin/conan'
results = root / 'results'
results.mkdir(exist_ok=True)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
command = [str(conan), 'install', '.', '--output-folder=build/conan',
           '--build=never', '-pr:h', 'profiles/macos-arm64', '--lockfile-out=conan.lock']

def disk_kib():
    return int(subprocess.check_output(['du', '-sk', str(root / '.deps')], text=True).split()[0])

before = disk_kib()
start = time.perf_counter()
with (results / f'{stamp}-conan.log').open('w') as log:
    result = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
elapsed = time.perf_counter() - start
report = {
    'timestamp_utc': stamp, 'system': platform.system(), 'architecture': platform.machine(),
    'conan_version': subprocess.check_output([str(conan), '--version'], text=True).strip(),
    'command': command, 'exit_code': result.returncode,
    'elapsed_seconds': round(elapsed, 3),
    'deps_before_kib': before, 'deps_after_kib': disk_kib(),
    'source_builds_allowed': False,
    'status': 'installed' if result.returncode == 0 else 'failed_inspect_log',
    'peak_disk_usage': 'not_measured',
}
(results / f'{stamp}-conan.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
print((results / f'{stamp}-conan.log').read_text()[-12000:])
raise SystemExit(result.returncode)
