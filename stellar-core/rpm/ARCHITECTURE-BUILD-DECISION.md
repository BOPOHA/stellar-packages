# Architecture Build Decision: Split Stellar Core's Rust build

- Status: Approved
- Date: 2026-10-09
- Decision owners: Stellar package maintainers
- Applies to: Stellar Core 29.x RPM and COPR builds

## Context

The Fedora 44 Mock build of `stellar-core-29.0.0-1.fc44` ran from
15:01:03 to 16:31:04 on an 8-CPU workstation: approximately 90 minutes.
PostgreSQL timestamps in the log place the functional test phase between
approximately 16:09 and 16:31, so compilation, linking, and installation took
about 68 minutes and `%check` took about 22 minutes.

The build log contains the following compilation workload:

| Component | Observed work in the old build |
| --- | ---: |
| Stellar Core C++ | 405 translation units |
| Stellar Core C++ tests included above | approximately 123 translation units |
| Bundled libsodium | 85 C translation units |
| Bundled xdrpp | 17 C++ translation units |
| gperftools and other bundled C++ dependencies | approximately 151 translation units |
| `cxxbridge-cmd` | 47 seconds |
| Soroban protocol hosts p21-p29 | approximately 13 minutes total |
| Final `librust_stellar_core.a` | 19 minutes 29 seconds |

The nine Soroban hosts are intentionally built as separate Rust dependency
graphs. Upstream passes each host and its dependency directory to the final
`cargo rustc` command. Splitting those internal `.rlib` files into RPMs would
therefore require packaging every `target/release/deps` tree and keeping the
Rust compiler, crate metadata, features, and code-generation flags identical.

The final C++ link already has a much cleaner boundary: it consumes one Rust
static library, `librust_stellar_core.a`, plus generated `RustBridge.h` and
`RustBridge.cpp`. That archive is the narrowest practical native interface
between the Rust and C++ builds.

The old 90-minute measurement is not a prediction for the optimized production
build. Release 2 already disables the C++ test sources and `%check` by default,
disables C++ LTO and discarded debug information, and changes Rust from full
LTO with one code-generation unit to ThinLTO with 16 code-generation units.
Nevertheless, a 1-2 CPU COPR worker can still make the Rust portion long enough
to justify an independently schedulable build.

## Decision

The approved packaging architecture has two source packages and build jobs:

```text
stellar-core-rust
    -> stellar-core-rust-static (architecture-specific RPM)
       - librust_stellar_core.a
       - RustBridge.h
       - RustBridge.cpp
       - build metadata

stellar-core
    BuildRequires exact stellar-core-rust-static version-release
    -> compiles production C/C++
    -> links the final stellar-core executable
```

`stellar-core-rust-static` is a private build artifact rather than a supported
public development API. Its RPM version and release must remain synchronized
with `stellar-core`. It is built separately for every target distribution and
architecture; it is not portable between Fedora, AlmaLinux, Amazon Linux, or
different CPU architectures.

The final package will support a prebuilt-Rust mode in the upstream Automake
files. In that mode, Cargo and the Soroban `.rlib` prerequisites are omitted
and the installed static archive and generated bridge sources are used
directly. Normal upstream source builds remain available when prebuilt-Rust
mode is not selected.

Production builds do not compile or execute the C++ test suite. A separate
explicit validation target retains the PostgreSQL and Soroban functional
tests. Validation builds may compile Rust in-tree because the test executable
requires the Rust `testutils` feature and is not the COPR production path.

Before relying only on the package split, the native build will also avoid two
known sources of unnecessary work:

1. Use the distribution `libsodium-devel` through upstream's existing
   pkg-config detection instead of compiling the 85 bundled C files.
2. Prevent bundled gperftools from adding its complete unit-test set to
   `noinst_PROGRAMS`; Stellar Core needs only `libtcmalloc_minimal.a`.

## Rejected alternatives

### One RPM subpackage inside `stellar-core.spec`

Rejected because all subpackages from one spec are produced by the same SRPM
build transaction. This would not split wall-clock time or the COPR timeout.

### One RPM for every Soroban protocol

Deferred unless `stellar-core-rust` itself exceeds the worker limit. This could
parallelize p21-p29 across workers, but it creates nine compiler-private RPM
interfaces containing `.rlib` files and complete dependency trees. A Rust
compiler update between producer and consumer builds could invalidate them.

### A C++ `stellar-core-devel` object package

Deferred. Upstream does not define a reusable `libstellar-core`; it links C++
objects directly into the executable. A static archive would require
whole-archive semantics to preserve registration-only objects, would expose a
private C++ ABI, and would need extensive Makefile changes. The Rust static
library is a substantially safer first split.

### Building once and repackaging the binary for every operating system

Rejected. The current binary is dynamically linked to glibc, libstdc++, and
the distribution PostgreSQL client library. The observed Fedora binary is
approximately 72 MiB and requires `libpq.so.private18-5`, among other symbol-
versioned system libraries. Native artifacts must be built in each target
chroot.

## Build and release workflow

For every enabled COPR chroot:

1. Build and publish `stellar-core-rust`.
2. Wait until `stellar-core-rust-static` is available to the project repository.
3. Build `stellar-core`, whose exact `BuildRequires` selects the matching Rust
   artifact.
4. Run the separate test-enabled build on an appropriately sized validation
   worker or locally; it is not part of the production COPR critical path.

Local Make targets must make the distinction explicit:

- build the Rust-static RPM;
- build the production Core RPM using the installed Rust-static RPM;
- optionally build the complete test-enabled package.

## Consequences

Benefits:

- Rust and C++ work are independently schedulable and independently retryable.
- The final Core build no longer downloads or compiles Cargo dependencies.
- A packaging-only change can rebuild the final RPM without rebuilding Rust.
- The selected boundary follows the artifact already used by upstream's final
  link rather than inventing an interface between Cargo crates.

Costs and constraints:

- COPR package publication order becomes significant.
- Rust and Core RPM version-release values must be updated together.
- The prebuilt archive remains specific to a distribution, architecture,
  compiler configuration, feature set, and Stellar Core source revision.
- Source or feature changes affecting the Rust bridge require rebuilding both
  packages.
- Validation builds still have a long path when the `testutils` feature is
  required.

## Follow-up criteria

Record clean wall-clock measurements for both new build jobs on local Mock and
COPR. Split p21-p29 only if the optimized `stellar-core-rust` build alone still
exceeds the worker timeout. Consider a private native dependency package only
if the optimized final C++ build independently exceeds the timeout after using
system libsodium and suppressing gperftools test binaries.
