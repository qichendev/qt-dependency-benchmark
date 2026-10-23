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

Initial repository scaffold. No Qt packages have been downloaded and no speed claims have been measured. Qt version, package configurations and binary sources must be selected after inspecting availability for the target platform.

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
