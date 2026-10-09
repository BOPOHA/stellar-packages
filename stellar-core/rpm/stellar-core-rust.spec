%global debug_package %{nil}
%global toolchain clang
%global _lto_cflags %{nil}

%bcond_without system_libsodium

# Keep this release synchronized with stellar-core.spec: the consumer uses an
# exact version-release BuildRequires.
Name: stellar-core-rust
Version: 29.0.0
Release: 3%{?dist}
Summary: Private Rust static build artifact for Stellar Core

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

BuildRequires: automake
BuildRequires: bison
BuildRequires: cargo >= 1.95
BuildRequires: clang >= 20
BuildRequires: flex
BuildRequires: git
BuildRequires: hostname
BuildRequires: libtool
BuildRequires: libunwind-devel
%if %{with system_libsodium}
BuildRequires: libsodium-devel >= 1.0.17
%endif
BuildRequires: pkgconfig
BuildRequires: postgresql-devel >= 13
BuildRequires: rust >= 1.95

%description
Source package for the private, architecture-specific Rust static library used
to link Stellar Core. It is split from the final executable build so COPR can
schedule and retry the expensive Rust and C++ phases independently.

%package static
Summary: Private Rust static library and CXX bridge for Stellar Core

%description static
Private build input containing Stellar Core's Rust static library and generated
CXX bridge. The contents are compiler-, feature-, distribution-, and
architecture-specific and are not a supported public development interface.

%prep
{{{ git_dir_setup_macro }}}
%setup -q -b 1 -T -D -n stellar-core-%{version}

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

%{__install} -d $HOME/.cargo
%{__install} -pm 0644 %{_builddir}/{{{ git_dir_name }}}/cargo-config.toml $HOME/.cargo/config.toml

%build
%set_build_flags
export CFLAGS="$CFLAGS -g0"
export CXXFLAGS="$CXXFLAGS -g0"
export RUSTFLAGS="$RUSTFLAGS -Cdebuginfo=0 -Ccodegen-units=16"
export CARGO_PROFILE_RELEASE_DEBUG=0
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
export CARGO_PROFILE_RELEASE_LTO=thin
%if 0%{?_with_compiler_cache}
export CC="ccache $CC"
export CXX="ccache $CXX"
export RUSTC_WRAPPER=sccache
%endif

NOGIT=legal-hack-to-work-with-local-files ./autogen.sh --skip-submodules yeah
%configure --disable-tests
%make_build -C src \
    ../target/release/librust_stellar_core.a \
    rust/RustBridge.h \
    rust/RustBridge.cpp \
    CARGO=cargo

%install
%{__install} -Dpm 0644 target/release/librust_stellar_core.a \
    %{buildroot}%{_libdir}/stellar-core-rust/%{version}/librust_stellar_core.a
%{__install} -Dpm 0644 src/rust/RustBridge.h \
    %{buildroot}%{_datadir}/stellar-core-rust/%{version}/RustBridge.h
%{__install} -Dpm 0644 src/rust/RustBridge.cpp \
    %{buildroot}%{_datadir}/stellar-core-rust/%{version}/RustBridge.cpp
%{__install} -d %{buildroot}%{_datadir}/stellar-core-rust/%{version}
{
    echo "stellar-core %{version}-%{release}"
    rustc -Vv
    cargo -V
    sha256sum target/release/librust_stellar_core.a
} > %{buildroot}%{_datadir}/stellar-core-rust/%{version}/build-info.txt

%check
test -s target/release/librust_stellar_core.a
test -s src/rust/RustBridge.h
test -s src/rust/RustBridge.cpp

%files static
%license COPYING
%{_libdir}/stellar-core-rust/%{version}/librust_stellar_core.a
%{_datadir}/stellar-core-rust/%{version}/RustBridge.h
%{_datadir}/stellar-core-rust/%{version}/RustBridge.cpp
%{_datadir}/stellar-core-rust/%{version}/build-info.txt

%changelog
* Fri Oct 09 2026 Anatolii Vorona <vorona.tolik@gmail.com> - 29.0.0-3
- split the production Rust static library from the final Stellar Core build
