# Findings and limits

**Update:** the [successful Conan run](conan-success.md) installs and runs Qt 6.11.1. The earlier missing-package results below are historical. The key mismatch was static versus shared dependency configuration; no version overrides were needed for the successful fuller Qt setup. libffi required a scoped compiler-version selection, documented with its validation limits.

## Conan availability

The [first check](conan-first-check.md) failed safely for the committed minimal Qt 6.8.3 options on macOS ARM64 / Apple Clang 17 / Release. This is an availability result, not an installation speed measurement.

ConanCenter has fuller Qt 6.8.3 binaries for this platform. HTTP HEAD requests on 2026-10-23 UTC returned the following `Content-Length` values for `conan_package.tgz`, without downloading archive bodies:

| Variant | Compressed bytes | MiB | Package revision |
| --- | ---: | ---: | --- |
| Shared | 16,928,462 | 16.14 | `9a6d11d4500de739b976e0c442569ddc` |
| Static | 32,661,621 | 31.15 | `1bd84f36183588c274bb4b1513df6536` |

Recipe revision: `df4192f9d91a5ad09f73537dd26d9eda`. Shared package ID: `fa5e6fc6461de2d0f9dfca14fc93ef0bbec052c6`; static package ID: `7c0a3a8aa088dcabf174ab047d516ca208e95fa9`. Raw query results are local at `results/qt-package-sizes.json`.

These figures exclude external dependencies, recipe metadata, extracted files, tool installations and temporary disk use. They are not final application sizes. Both binaries enable GUI and Widgets. A default-options shared graph query also reported a missing Qt binary: current dependency resolution does not automatically reproduce the versions used by the published binary. A matching dependency graph or lockfile must be resolved before claiming installability or total download size.

## Deployment

An application linking only `Qt6::Core` does not automatically need to ship QtGui or QtWidgets because they were present in the downloaded development package. With shared linking, distribute the actual runtime libraries and required plugins, including their non-system runtime dependencies. With static linking, Qt code is incorporated into the executable; any remaining dynamic dependencies still need inspection.

Headers, package caches and build tools are not generally runtime deployment inputs. Inspect the built executable and its transitive libraries, rather than copying the entire Conan or vcpkg installation. On macOS use `otool -L`; Qt app bundles can use `macdeployqt` when available. Our smoke application has not yet been built, so its actual runtime dependency list is unverified.

References: [Qt deployment](https://doc.qt.io/qt-6/deployment.html), [Qt 6.8 macOS deployment](https://doc.qt.io/qt-6.8/macos-deployment.html).

## Benchmark interpretation

The [first vcpkg check](vcpkg-first-check.md) also failed without building dependencies: an explicitly empty, read-only binary cache restored zero packages. It ran compiler detection and downloaded Ninja. Its 30.980-second failure is not comparable to Conan's 3.583-second availability failure as a successful install benchmark.

Keep download bytes, extracted installation size, development disk use and shipped application size separate. Missing-binary failures cannot be ranked as successful installation performance. A successful Conan-versus-vcpkg comparison also requires matching build configurations and accessible binary sources for both tools.
