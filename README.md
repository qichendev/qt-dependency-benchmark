# Qt dependency benchmark

Compare Conan 2 and vcpkg manifest dependency acquisition without building any dependency from source. Missing binaries are failures, never successful benchmark results.

## Rules

- Conan: `conan install . --build=never`.
- vcpkg: `vcpkg install --only-binarycaching`.
- All dependency installations and caches belong under `.deps/`.
- A vcpkg registry is not a public binary cache: provide an existing compatible binary cache to test a successful restore.
- Use identical Qt versions, modules, architecture, compiler, linkage and build configuration before comparing successful runs. Package defaults are not equivalent.
- Record binary availability, wall time, installed size, peak disk use and cleanup residue separately. Do not rank failed installs by speed.

## Status

**Conan binary-only installation and the Qt Core smoke test now pass on macOS ARM64.** See the [successful Conan run](docs/conan-success.md) for the working profile, disk use and limitations. vcpkg testing is paused.

The current smoke application links only `Qt6::Core` from Qt 6.11.1. Conan uses fuller published binaries, including GUI and Widgets. All dependency libraries with a `shared` option use shared linking. The original minimal 6.8.3 Conan configuration is preserved at `profiles/conan-minimal-original.txt`; historical [findings](docs/findings.md) and the [vcpkg check](docs/vcpkg-first-check.md) describe earlier experiments. The archived vcpkg manifest remains at 6.8.3 and is not equivalent to the active Conan configuration.

The host profile uses Apple Clang 17, with a package-specific Apple Clang 13 selection for the published libffi C library. This run verifies Qt Core only, not GUI, GLib or libffi functionality. Do not treat that exception as general cross-compiler compatibility.

### Conan 2

For this macOS ARM64 configuration, run from this directory:

```sh
python3 -m venv .deps/tools/conan
.deps/tools/conan/bin/python -m pip install --no-cache-dir --only-binary=:all: conan==2.33.0
export CONAN_HOME="$PWD/.deps/conan"
.deps/tools/conan/bin/conan profile detect
.deps/tools/conan/bin/python scripts/try_conan.py
cmake -S . -B build/conan -DCMAKE_TOOLCHAIN_FILE="$PWD/build/conan/conan_toolchain.cmake" -DCMAKE_BUILD_TYPE=Release
cmake --build build/conan --config Release
ctest --test-dir build/conan -C Release --output-on-failure
```

Stop if installation fails. Never add `--build=missing`.

### Local deployment package

After building, run `python3 scripts/package_macos.py`. It creates a ZIP under `results/`, copies only the four non-system runtime libraries and their package notices, fixes load paths, ad-hoc signs the copies, and validates execution after extracting the ZIP elsewhere. The [measured archive](docs/package-size.md) is 3.05 MiB compressed / 8.37 MiB extracted file bytes. It is not a notarized public release.

### Archived vcpkg manifest experiment

These commands reproduce the earlier dependency acquisition attempt. The current application requires Qt 6.11.1, so building it against this archived 6.8.3 manifest will fail the version check. No populated vcpkg binary source is configured.

An existing compatible binary cache is required. With the vcpkg tool under `.deps/tools/vcpkg` and binary archives under `.deps/binary-cache`:

```sh
mkdir -p .deps/binary-cache .deps/downloads .deps/registry-cache
export VCPKG_DOWNLOADS="$PWD/.deps/downloads"
export VCPKG_REGISTRIES_CACHE="$PWD/.deps/registry-cache"
export VCPKG_BINARY_SOURCES="clear;files,$PWD/.deps/binary-cache,read"
.deps/tools/vcpkg/vcpkg install --only-binarycaching --x-install-root="$PWD/.deps/installed"
cmake -S . -B build/vcpkg -DCMAKE_TOOLCHAIN_FILE="$PWD/.deps/tools/vcpkg/scripts/buildsystems/vcpkg.cmake" -DVCPKG_INSTALLED_DIR="$PWD/.deps/installed" -DCMAKE_BUILD_TYPE=Release
cmake --build build/vcpkg --config Release
ctest --test-dir build/vcpkg -C Release --output-on-failure
```

An empty cache should fail without compiling dependencies. CMake also sets `VCPKG_INSTALL_OPTIONS=--only-binarycaching` before loading the toolchain. The application itself is compiled normally.

Run the read-only environment check:

```sh
python3 scripts/check_environment.py
```

Keep tool installations under `.deps/tools/` when setting up the actual benchmark. Set `CONAN_HOME` to the absolute project `.deps/conan` path; configure vcpkg download, registry, binary and installation paths explicitly. Merely using manifest mode does not isolate caches.

## As a submodule

```sh
git submodule update --init packages/qt-dependency-benchmark
```

This repository has its own history. Commit and push changes here first, then commit the updated submodule pointer in the parent repository. Avoid recursive initialization of unrelated submodules.
