"""Query latest-recipe binary metadata only, without downloading Qt archives."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
env = dict(os.environ, CONAN_HOME=str(root / '.deps/conan'))
tool = root / '.deps/tools/conan/bin/conan'
results = root / 'results'
results.mkdir(exist_ok=True)
versions = json.loads((results / 'qt-versions.json').read_text())['conancenter']

def query(ref):
    proc = subprocess.run([str(tool), 'list', ref + ':*', '-r=conancenter', '--format=json'],
                          cwd=root, env=env, capture_output=True, text=True)
    if proc.returncode:
        return dict(ref=ref, error=proc.stderr)
    data = json.loads(proc.stdout)
    (results / (ref.replace('/', '-') + '-binaries.json')).write_text(json.dumps(data, indent=2))
    packages = []
    revisions = data.get('conancenter', {}).get(ref, {}).get('revisions', {})
    for revision, value in revisions.items():
        for pid, package in value.get('packages', {}).items():
            info = package.get('info', {})
            packages.append(dict(id=pid, revision=revision, **info))
    mac = [p for p in packages if p.get('settings', {}).get('os') == 'Macos'
           and p.get('settings', {}).get('arch') == 'armv8']
    minimal = [p for p in mac if p.get('options', {}).get('gui') == 'False'
               and p.get('options', {}).get('widgets') == 'False']
    return dict(ref=ref, total=len(packages), mac_arm=len(mac),
                mac_arm_no_gui_widgets=len(minimal),
                compilers=sorted({p['settings'].get('compiler.version', '') for p in mac}),
                release_shared=sum(p['settings'].get('build_type') == 'Release'
                                   and p.get('options', {}).get('shared') == 'True' for p in mac))

if __name__ == '__main__':
    refs = [v for v in versions if v.startswith('qt/6.')]
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(query, refs))
    (results / 'qt-version-comparison.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps(rows, indent=2))
