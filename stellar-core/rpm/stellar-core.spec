%global debug_package %{nil}
%global toolchain clang
%global _lto_cflags %{nil}
%define system_name stellar

# Building Stellar Core's test suite adds roughly one third more C++ sources
# and enables Rust test utilities. Keep release builds lean; use --with tests
# for a dedicated validation build.
%bcond_with tests

# Full Rust LTO is extremely expensive because Stellar Core builds a separate
# Soroban host for every supported protocol. ThinLTO preserves cross-crate
# optimization while keeping clean COPR builds below the worker timeout.
%bcond_with full_rust_lto

# Prefer the distribution ABI and avoid rebuilding bundled libsodium. Chroots
# without libsodium-devel can explicitly select the bundled fallback.
%bcond_without system_libsodium

# Use the distribution toolchain by default. The bundled installer remains
# available with --without enabled_system_rust for pinned-toolchain builds.
%bcond_without enabled_system_rust
%if %{with enabled_system_rust}
%global cargo_override CARGO=cargo
%endif

Name: stellar-core
Version: 29.0.0
Release: 3%{?dist}
Summary: Stellar is a decentralized, federated peer-to-peer network

License: Apache-2.0
URL: https://github.com/stellar/stellar-core
Source0: {{{ git_dir_pack }}}
Source1: https://github.com/stellar/stellar-core/archive/refs/tags/v%{version}.tar.gz#/stellar-core-v%{version}.tar.gz
Patch0: patch-001.patch
Patch1: patch-002-prebuilt-rust.patch
# START: submodule sources
Source100: https://api.github.com/repos/stellar/libsodium/tarball/71d227cf8e4644393a3322f36050f7afdfddc498#/stellar-libsodium-71d227c.tar.gz
Source101: https://api.github.com/repos/xdrpp/xdrpp/tarball/a29a1703699ad2b6cb4b28538d6ed4173eacdb60#/xdrpp-xdrpp-a29a170.tar.gz
Source102: https://api.github.com/repos/stellar/medida/tarball/2bf1afac2911c9aca9d1ba06e3d883fa150c9baf#/stellar-medida-2bf1afa.tar.gz
Source103: https://api.github.com/repos/USCiLab/cereal/tarball/ebef1e929807629befafbb2918ea1a08c7194554#/USCiLab-cereal-ebef1e9.tar.gz
Source104: https://api.github.com/repos/chriskohlhoff/asio/tarball/c465349fa5cd91a64bb369f5131ceacab2c0c1c3#/chriskohlhoff-asio-c465349.tar.gz
Source105: https://api.github.com/repos/fmtlib/fmt/tarball/407c905e45ad75fc29bf0f9bb7c5c2fd3475976f#/fmtlib-fmt-407c905.tar.gz
Source106: https://api.github.com/repos/stellar/tracy/tarball/29d05d1a33115bc451cad068225c96aa5ad7051d#/stellar-tracy-29d05d1.tar.gz
Source107: https://api.github.com/repos/gabime/spdlog/tarball/79524ddd08a4ec981b7fea76afd08ee05f83755d#/gabime-spdlog-79524dd.tar.gz
Source108: https://api.github.com/repos/stellar/stellar-xdr/tarball/9c9c145953e80990d6ff1ae3a6a973a0ce6d0694#/stellar-stellar-xdr-9c9c145.tar.gz
Source109: https://api.github.com/repos/stellar/rs-soroban-env/tarball/7eeddd897cfb0f700f938b0c8d6f0541150d1fcb#/stellar-rs-soroban-env-7eeddd8.tar.gz
Source110: https://api.github.com/repos/stellar/rs-soroban-env/tarball/1cd8b8dca9aeeca9ce45b129cd923992b32dc258#/stellar-rs-soroban-env-1cd8b8d.tar.gz
Source111: https://api.github.com/repos/stellar/rs-soroban-env/tarball/688bc34e6cd15c71742139e625268c7f30f55a92#/stellar-rs-soroban-env-688bc34.tar.gz
Source112: https://api.github.com/repos/stellar/rs-soroban-env/tarball/a37eeda815e626f416eff13f2eacb32a8b0c3729#/stellar-rs-soroban-env-a37eeda.tar.gz
Source113: https://api.github.com/repos/stellar/rs-soroban-env/tarball/6323c1fc03ecb9f53b7c1e42fd62c1bbd3aebc2c#/stellar-rs-soroban-env-6323c1f.tar.gz
Source114: https://api.github.com/repos/stellar/rs-soroban-env/tarball/b351f88a468d3b9e1d6de53d5b0ca585f6b7dadb#/stellar-rs-soroban-env-b351f88.tar.gz
Source115: https://api.github.com/repos/stellar/rs-soroban-env/tarball/b03d2563f3a08d51095a19bdbb6d90364b8ce04a#/stellar-rs-soroban-env-b03d256.tar.gz
Source116: https://api.github.com/repos/stellar/rs-soroban-env/tarball/ba37ea5f76a10710835992fb90f9ec7a14eca499#/stellar-rs-soroban-env-ba37ea5.tar.gz
Source117: https://api.github.com/repos/stellar/rs-soroban-env/tarball/a721944b5a4ea830a4bf5c2dbb8dbe8c1e1354c5#/stellar-rs-soroban-env-a721944.tar.gz
Source118: https://api.github.com/repos/gperftools/gperftools/tarball/6ed73507dd3970a123e267a50b3ee73392e3b053#/gperftools-gperftools-6ed7350.tar.gz
# END: submodule sources
BuildRequires: clang >= 20
BuildRequires: postgresql-devel >= 13
%if %{with system_libsodium}
BuildRequires: libsodium-devel >= 1.0.17
%endif
%if %{with tests}
BuildRequires: postgresql-server >= 13
BuildRequires: tzdata
%else
BuildRequires: stellar-core-rust-static = %{version}-%{release}
%endif

Requires: user(stellar)
Requires: group(stellar)

BuildRequires: automake
BuildRequires: bison
%if %{with tests}
%if %{with enabled_system_rust}
BuildRequires: cargo >= 1.95
BuildRequires: rust >= 1.95
%else
BuildRequires: curl
BuildRequires: perl
%endif
%endif
BuildRequires: flex
BuildRequires: git
BuildRequires: hostname
BuildRequires: libtool
BuildRequires: libunwind-devel
%if %{with tests}
BuildRequires: parallel
%endif
BuildRequires: pkgconfig
BuildRequires: systemd-rpm-macros

Provides: %{name} = %{version}

%description
Stellar is a decentralized, federated peer-to-peer network that allows people
to send payments in any asset anywhere in the world instantaneously and with a
minimal fee. Stellar Core is its C++ implementation of the Stellar Consensus
Protocol, configured to construct a chain of ledgers that agree across all
participating nodes.

%prep
{{{ git_dir_setup_macro }}}
%setup -q -b 1 -T -D -n %{name}-%{version}
sed -i "s|\x25\x25VERSION\x25\x25|%{version}-%{release}|" src/main/StellarCoreVersion.cpp.in

# START: submodules setup
tar -zxf %{SOURCE100} --strip-components 1 -C lib/libsodium/
tar -zxf %{SOURCE101} --strip-components 1 -C lib/xdrpp/
tar -zxf %{SOURCE102} --strip-components 1 -C lib/libmedida/
tar -zxf %{SOURCE103} --strip-components 1 -C lib/cereal/
tar -zxf %{SOURCE104} --strip-components 1 -C lib/asio/
tar -zxf %{SOURCE105} --strip-components 1 -C lib/fmt/
tar -zxf %{SOURCE106} --strip-components 1 -C lib/tracy/
tar -zxf %{SOURCE107} --strip-components 1 -C lib/spdlog/
tar -zxf %{SOURCE108} --strip-components 1 -C src/protocol-curr/xdr/
tar -zxf %{SOURCE109} --strip-components 1 -C src/rust/soroban/p21/
echo '7eeddd897cfb0f700f938b0c8d6f0541150d1fcb' > src/rust/soroban/p21/.git-revision
tar -zxf %{SOURCE110} --strip-components 1 -C src/rust/soroban/p22/
echo '1cd8b8dca9aeeca9ce45b129cd923992b32dc258' > src/rust/soroban/p22/.git-revision
tar -zxf %{SOURCE111} --strip-components 1 -C src/rust/soroban/p23/
echo '688bc34e6cd15c71742139e625268c7f30f55a92' > src/rust/soroban/p23/.git-revision
tar -zxf %{SOURCE112} --strip-components 1 -C src/rust/soroban/p24/
echo 'a37eeda815e626f416eff13f2eacb32a8b0c3729' > src/rust/soroban/p24/.git-revision
tar -zxf %{SOURCE113} --strip-components 1 -C src/rust/soroban/p25/
echo '6323c1fc03ecb9f53b7c1e42fd62c1bbd3aebc2c' > src/rust/soroban/p25/.git-revision
tar -zxf %{SOURCE114} --strip-components 1 -C src/rust/soroban/p26/
echo 'b351f88a468d3b9e1d6de53d5b0ca585f6b7dadb' > src/rust/soroban/p26/.git-revision
tar -zxf %{SOURCE115} --strip-components 1 -C src/rust/soroban/p27/
echo 'b03d2563f3a08d51095a19bdbb6d90364b8ce04a' > src/rust/soroban/p27/.git-revision
tar -zxf %{SOURCE116} --strip-components 1 -C src/rust/soroban/p28/
echo 'ba37ea5f76a10710835992fb90f9ec7a14eca499' > src/rust/soroban/p28/.git-revision
tar -zxf %{SOURCE117} --strip-components 1 -C src/rust/soroban/p29/
echo 'a721944b5a4ea830a4bf5c2dbb8dbe8c1e1354c5' > src/rust/soroban/p29/.git-revision
tar -zxf %{SOURCE118} --strip-components 1 -C lib/gperftools/
# END: submodules setup

%patch -P 0 -p1
%patch -P 1 -p1

%if %{with tests}
%if %{without enabled_system_rust}
./install-rust.sh
%endif

%{__install} -d $HOME/.cargo
%{__install} -pm 0644 %{_builddir}/{{{ git_dir_name }}}/cargo-config.toml $HOME/.cargo/config.toml
%else
%{__install} -pm 0644 %{_datadir}/stellar-core-rust/%{version}/RustBridge.h src/rust/RustBridge.h
%{__install} -pm 0644 %{_datadir}/stellar-core-rust/%{version}/RustBridge.cpp src/rust/RustBridge.cpp
%endif

%build

%if %{without enabled_system_rust}
source "$HOME/.cargo/env"
%endif

%set_build_flags
# This package intentionally does not produce debuginfo subpackages. Avoid
# spending time and disk space generating DWARF that RPM will discard.
export CFLAGS="$CFLAGS -g0"
export CXXFLAGS="$CXXFLAGS -g0"
export RUSTFLAGS="$RUSTFLAGS -Cdebuginfo=0"
export CARGO_PROFILE_RELEASE_DEBUG=0
%if %{without full_rust_lto}
export RUSTFLAGS="$RUSTFLAGS -Ccodegen-units=16"
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
export CARGO_PROFILE_RELEASE_LTO=thin
%endif
%if 0%{?_with_compiler_cache}
# This is enabled only by the local `make rpmbuild` target. Keep Mock builds
# unchanged while allowing fresh rpmbuild trees to reuse C/C++ and Rust
# compilation.
export CC="ccache $CC"
export CXX="ccache $CXX"
export RUSTC_WRAPPER=sccache
%endif
NOGIT=legal-hack-to-work-with-local-files ./autogen.sh --skip-submodules yeah
%if %{with tests}
%configure
%else
%configure \
    --disable-tests \
    --with-prebuilt-rust=%{_libdir}/stellar-core-rust/%{version}/librust_stellar_core.a
%endif
%make_build %{?cargo_override}

%install
%make_install %{?cargo_override}
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.service   %{buildroot}%{_unitdir}/%{name}.service
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}@.service  %{buildroot}%{_unitdir}/%{name}@.service
%{__install} -Dpm 0644 %{buildroot}%{_docdir}/%{name}/stellar-core_example.cfg %{buildroot}%{_sysconfdir}/stellar/%{name}.cfg

%{__install} -d %{buildroot}/var/log/stellar
%{__install} -d %{buildroot}/var/lib/stellar/core
%{__install} -d %{buildroot}%{_sysconfdir}/stellar

%check
%if %{with tests}
# The release archive is not a Git checkout, so check-nondet and
# check-nocstyle cannot run in an SRPM build.  The backtrace test requires
# function-name symbolization that is not reliable with distro LTO flags.
# Keep the PostgreSQL functional suite (including check-sorobans).
INTERACTIVE=0 TEST_SPEC='~[acceptance]~[.]~[backtrace]' \
    make check TESTS=test/selftest-pg %{?cargo_override}
%endif

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%{_bindir}/%{name}
%dir %{_docdir}/%{name}/
%doc %{_docdir}/%{name}/*
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%config(noreplace) %{_sysconfdir}/stellar/%{name}.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %attr(0755, stellar, stellar) /var/log/stellar
%dir %attr(0755, stellar, stellar) /var/lib/stellar/core

%changelog
* Fri Oct 09 2026 Anatolii Vorona <vorona.tolik@gmail.com> - 29.0.0-3
- update v29.0.0; require C++20 and Rust 1.95 toolchains
- streamline production builds by excluding tests and discarded debug data
- use Rust ThinLTO and disable C++ LTO to fit clean builds within COPR limits
- consume the separately built Rust static library in production builds
- use system libsodium and omit vendored gperftools test executables

* Sat Mar 02 2024 Anatolii Vorona <vorona.tolik@gmail.com>
- update v20.3.0

* Fri Jan 12 2024 Anatolii Vorona <vorona.tolik@gmail.com>
- update v20.1.0

* Sat Dec 23 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v20.0.2; protocol version 21

* Sat Sep 23 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.14.0 (overlay improvements for tracking, logging, monitoring)

* Tue Sep 19 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.13.0

* Tue Apr 25 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v2.24.1

* Tue Mar 21 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.8.0

* Wed Feb 22 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- mass rebuild v19.7.0 with patch for fc38 and rawhide (Clang 15 and GCC 13)

* Thu Feb 9 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.7.0

* Tue Dec 6 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.6.0

* Wed Nov 2 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.5.0

* Wed Oct 12 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.4.0

* Mon Aug  1 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.3.0

* Sun Jul 31 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.2.0
- postgresql libs should be >= 13

* Mon Jun 06 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.1.0

* Wed Mar 23 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- init stellar-core rpm
