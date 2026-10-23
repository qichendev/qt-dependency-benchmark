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

The initial smoke application links only `Qt6::Core`, pinned to Qt 6.8.3 in CMake and both dependency manifests. It prints and checks the runtime Qt version. The [first Conan check](docs/conan-first-check.md) found no binary matching the minimal options and failed without building dependencies. No Qt library has been installed and no successful installation speed has been measured.

Conan disables GUI, Widgets and several optional integrations. vcpkg disables default features. These are starting configurations, **not equivalent package builds**: recipes can still include other Qt Base libraries or enable platform requirements transitively (for example macOS dependencies). A Core-only application does not guarantee a small Core-only binary download. Custom options can also reduce the availability of prebuilt Conan packages.

### Conan 2

After installing Conan 2, run from this directory:

```sh
export CONAN_HOME="$PWD/.deps/conan"
conan profile detect
conan install . --output-folder=build/conan --build=never -s build_type=Release -s compiler.cppstd=17
cmake -S . -B build/conan -DCMAKE_TOOLCHAIN_FILE="$PWD/build/conan/conan_toolchain.cmake" -DCMAKE_BUILD_TYPE=Release
cmake --build build/conan --config Release
ctest --test-dir build/conan -C Release --output-on-failure
```

Stop if installation fails. Never add `--build=missing`.

### vcpkg manifest

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
