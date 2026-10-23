# First binary-only check

Run: 2026-10-23 UTC, macOS ARM64, Apple Clang 17, Release, C++17, Conan 2.33.0.

`scripts/try_conan.py` ran `conan install . --build=never` with the committed minimal options and a fresh project-local Conan home. It failed with missing Qt binary ID `5245b8c8acfabec8f277ebf2881d71d343d5c0e8`.

- Wall time: 3.583 seconds. This is a failed availability check, not installation performance.
- `.deps` allocated size before: 29,120 KiB; after: 29,404 KiB (includes the isolated Python environment and Conan tool).
- No Qt sources were downloaded or compiled; no Qt binary was installed.
- Peak disk use was not measured.
- Raw local logs and JSON are ignored under `results/`.

The remote package metadata for Qt 6.8.3 recipe revision `df4192f9d91a5ad09f73537dd26d9eda` contained two macOS ARM64 Release / Apple Clang 17 binaries: static `7c0a3a8aa088dcabf174ab047d516ca208e95fa9` and shared `fa5e6fc6461de2d0f9dfca14fc93ef0bbec052c6`. Both enable GUI, Widgets and additional integrations. Neither matches the committed minimal configuration. Their full dependency graphs and download sizes were not tested.

Conclusion: this remote has binaries for the platform, but not for these minimal options. Reusing a fuller binary would keep the application Core-only while increasing acquired dependencies. Keep the minimal configuration unchanged until that tradeoff is chosen. This does not establish that Qt binaries are unavailable for macOS, or that Conan cannot install Qt.

## Reproduce

```sh
python3 -m venv .deps/tools/conan
.deps/tools/conan/bin/python -m pip install --no-cache-dir --only-binary=:all: conan==2.33.0
export CONAN_HOME="$PWD/.deps/conan"
.deps/tools/conan/bin/conan profile detect
.deps/tools/conan/bin/python scripts/try_conan.py
.deps/tools/conan/bin/conan list 'qt/6.8.3:*' -r=conancenter --format=json --out-file=results/qt-6.8.3-packages.json
```

Profile detection and remote recipe state may change. See the settings and recipe revision above when comparing later results. All installed tool and dependency state for this run is under `.deps/`; logs are under `results/`.
