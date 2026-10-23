"""Create and measure a local relocatable ARM64 CLI archive; never uploads it."""
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

root = Path(__file__).resolve().parents[1]
exe = root / 'build/conan/qt_core_smoke'

def output(*args):
    return subprocess.check_output(args, text=True)

def dependencies(path):
    return [line.strip().split(' (compatibility')[0]
            for line in output('otool', '-L', str(path)).splitlines()[1:]]

def rpaths(path):
    return re.findall(r'cmd LC_RPATH\s+cmdsize \d+\s+path (.*?) \(offset',
                      output('otool', '-l', str(path)))

search = [Path(p) for p in rpaths(exe)]
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
destination = root / 'results' / f'package-{stamp}'
bundle = destination / 'qt-core-smoke-macos-arm64'
(bundle / 'bin').mkdir(parents=True)
(bundle / 'lib').mkdir()
shutil.copy2(exe, bundle / 'bin/qt_core_smoke')
pending = [exe]
sources = {}
while pending:
    source = pending.pop()
    for dep in dependencies(source):
        if dep.startswith(('/usr/lib/', '/System/Library/')):
            continue
        if dep.startswith('@rpath/'):
            candidates = [p / dep.removeprefix('@rpath/') for p in search]
        elif dep.startswith('@loader_path/'):
            candidates = [source.parent / dep.removeprefix('@loader_path/')]
        elif dep.startswith('/'):
            candidates = [Path(dep)]
        else:
            raise RuntimeError(f'Unsupported dependency: {dep}')
        found = next((p.resolve() for p in candidates if p.is_file()), None)
        if found is None:
            raise RuntimeError(f'Unresolved dependency: {dep}')
        name = dep.split('/')[-1]
        if name in sources:
            if sources[name] != found:
                raise RuntimeError(f'Conflicting library name: {name}')
            continue
        sources[name] = found
        shutil.copy2(found, bundle / 'lib' / name)
        pending.append(found)

# Copy package-provided notices, without claiming this is a license compliance audit.
for name, source in sources.items():
    package = source.parent.parent
    licenses = package / 'licenses'
    if not licenses.is_dir():
        raise RuntimeError(f'Missing license directory for {source}')
    shutil.copytree(licenses, bundle / 'licenses' / name)

for path in [*(bundle / 'lib').iterdir(), bundle / 'bin/qt_core_smoke']:
    # Rewrite every non-system load command, including dylib IDs, to local paths.
    for dep in dependencies(path):
        if dep.startswith(('/usr/lib/', '/System/Library/')):
            continue
        name = dep.split('/')[-1]
        if name not in sources:
            raise RuntimeError(f'Unexpected dependency: {dep}')
        replacement = ('@loader_path/../lib/' if path.parent.name == 'bin'
                       else '@loader_path/') + name
        subprocess.run(['install_name_tool', '-change', dep, replacement, str(path)], check=True)
    for old in rpaths(path):
        subprocess.run(['install_name_tool', '-delete_rpath', old, str(path)], check=True)
    if path.parent.name == 'lib':
        subprocess.run(['install_name_tool', '-id', '@loader_path/' + path.name, str(path)], check=True)
    subprocess.run(['codesign', '--force', '--sign', '-', str(path)], check=True, capture_output=True)
    subprocess.run(['codesign', '--verify', '--strict', str(path)], check=True)

archive = destination / (bundle.name + '.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for path in sorted(bundle.rglob('*')):
        if path.is_file():
            z.write(path, path.relative_to(destination))

# Test the ZIP itself after extraction at a different path with dyld overrides removed.
with tempfile.TemporaryDirectory(prefix='qt-release-check-') as tmp:
    subprocess.run(['/usr/bin/ditto', '-x', '-k', str(archive), tmp], check=True)
    moved = Path(tmp) / bundle.name
    env = {k: v for k, v in os.environ.items() if not k.startswith(('DYLD_', 'CONAN_'))}
    env['DYLD_PRINT_LIBRARIES'] = '1'
    run = subprocess.run([str(moved / 'bin/qt_core_smoke')], cwd=tmp, env=env,
                         capture_output=True, text=True, check=True)
    if str(root / '.deps') in run.stderr:
        raise RuntimeError('Relocated process loaded from the dependency cache')
    (destination / 'relocated-run.log').write_text(run.stdout + run.stderr)

files = {str(p.relative_to(bundle)): p.stat().st_size for p in bundle.rglob('*') if p.is_file()}
report = dict(timestamp_utc=stamp, zip_bytes=archive.stat().st_size,
              unpacked_file_bytes=sum(files.values()),
              allocated_kib=int(output('du', '-sk', str(bundle)).split()[0]),
              runtime_library_count=len(sources), files=files,
              relocated_zip_test=run.stdout.strip(), signing='local ad-hoc; not notarized')
(destination / 'size-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))
print(f'Archive: {archive}')
