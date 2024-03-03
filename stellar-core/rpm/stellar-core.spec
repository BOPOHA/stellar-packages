%global debug_package %{nil}
%global toolchain clang
%define system_name stellar

%if 0%{?fc38}%{?fc39}
# initializes global with_enabled_system_rust to 1
%bcond_without enabled_system_rust
%else
%bcond_with enabled_system_rust
%endif

Name: stellar-core
Version: 20.3.0
Release: 1%{?dist}
Summary: Stellar is a decentralized, federated peer-to-peer network

License: Apache 2.0
Source0: {{{ git_dir_pack }}}
Source1: https://github.com/stellar/stellar-core/archive/refs/tags/v%{version}.tar.gz#/stellar-core-v%{version}.tar.gz
# START: submodule sources
Source100: https://api.github.com/repos/chriskohlhoff/asio/tarball/c465349fa5cd91a64bb369f5131ceacab2c0c1c3#/chriskohlhoff-asio-asio-1-28-0-0-gc465349.tar.gz
Source101: https://api.github.com/repos/USCiLab/cereal/tarball/ebef1e929807629befafbb2918ea1a08c7194554#/USCiLab-cereal-v1.3.2-0-gebef1e9.tar.gz
Source102: https://api.github.com/repos/fmtlib/fmt/tarball/f5e54359df4c26b6230fc61d38aa294581393084#/fmtlib-fmt-10.1.1-0-gf5e5435.tar.gz
Source103: https://api.github.com/repos/stellar/medida/tarball/f91354b0055de939779d392999975d611b1b1ad5#/stellar-medida-f91354b.tar.gz
Source104: https://api.github.com/repos/stellar/libsodium/tarball/71d227cf8e4644393a3322f36050f7afdfddc498#/stellar-libsodium-vs2022-0-g71d227c.tar.gz
Source105: https://api.github.com/repos/gabime/spdlog/tarball/7e635fca68d014934b4af8a1cf874f63989352b7#/gabime-spdlog-v1.12.0-0-g7e635fc.tar.gz
Source106: https://api.github.com/repos/stellar/tracy/tarball/897aec5b062664d2485f4f9a213715d2e527e0ca#/stellar-tracy-v0.6.3-3431-g897aec5.tar.gz
Source107: https://api.github.com/repos/xdrpp/xdrpp/tarball/9fd7ca222bb26337e1443c67b18fbc5019962884#/xdrpp-xdrpp-9fd7ca2.tar.gz
Source108: https://api.github.com/repos/stellar/stellar-xdr/tarball/b96148cd4acc372cc9af17b909ffe4b12c43ecb6#/stellar-stellar-xdr-v20.1-0-gb96148c.tar.gz
Source109: https://api.github.com/repos/stellar/stellar-xdr/tarball/6a71b137bc49f901bed53c8c215c26213017026c#/stellar-stellar-xdr-6a71b13.tar.gz

# END: submodule sources
%if 0%{?el7}
BuildRequires: llvm-toolset-14.0-clang
BuildRequires: rh-postgresql13-postgresql-devel, rh-postgresql13-postgresql-server
%else
BuildRequires: clang >= 12
BuildRequires: postgresql-devel >= 13
BuildRequires: postgresql-server >= 13
%endif

Requires: user(stellar)
Requires: group(stellar)

BuildRequires: automake
BuildRequires: bison
%if %{with enabled_system_rust}
BuildRequires: cargo
%endif
BuildRequires: flex
BuildRequires: git
BuildRequires: hostname
BuildRequires: libtool
BuildRequires: libunwind-devel
BuildRequires: parallel
BuildRequires: systemd-rpm-macros

Provides: %{name} = %{version}

%description
Stellar is a decentralized, federated peer-to-peer network that allows people to send payments in any asset
anywhere in the world instantaneously, and with minimal fee. Stellar-core is the core component of this network.
Stellar-core is a C++ implementation of the Stellar Consensus Protocol configured to construct a chain of ledgers
that are guaranteed to be in agreement across all the participating nodes at all times.

%prep
{{{ git_dir_setup_macro }}}
%setup -q -b 1 -T -D -n %{name}-%{version}
sed -i "s|\x25\x25VERSION\x25\x25|%{version}-%{release}|" src/main/StellarCoreVersion.cpp.in

# START: submodules setup
tar -zxf  %{SOURCE100} --strip-components 1 -C lib/asio/
tar -zxf  %{SOURCE101} --strip-components 1 -C lib/cereal/
tar -zxf  %{SOURCE102} --strip-components 1 -C lib/fmt/
tar -zxf  %{SOURCE103} --strip-components 1 -C lib/libmedida/
tar -zxf  %{SOURCE104} --strip-components 1 -C lib/libsodium/
tar -zxf  %{SOURCE105} --strip-components 1 -C lib/spdlog/
tar -zxf  %{SOURCE106} --strip-components 1 -C lib/tracy/
tar -zxf  %{SOURCE107} --strip-components 1 -C lib/xdrpp/
tar -zxf  %{SOURCE108} --strip-components 1 -C src/protocol-curr/xdr/
tar -zxf  %{SOURCE109} --strip-components 1 -C src/protocol-next/xdr/

# END: submodules setup

%if %{without enabled_system_rust}
%if 0%{?el7}
    source /opt/rh/llvm-toolset-14.0/enable
%endif
./install-rust.sh
%endif

mkdir -p $HOME/.cargo && cp %{_builddir}/{{{ git_dir_name }}}/cargo-config.toml $HOME/.cargo/config.toml

%build

%if %{without enabled_system_rust}
source "$HOME/.cargo/env"
%endif

%if 0%{?el7}
    LDFLAGS=-Wl,-rpath,%{_datadir}/%{system_name}/lib/
    source /opt/rh/rh-postgresql13/enable
    source /opt/rh/llvm-toolset-14.0/enable
%endif
%set_build_flags
NOGIT=legal-hack-to-work-with-local-files ./autogen.sh --skip-submodules yeah
%configure
%make_build

%install
%make_install
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.service   %{buildroot}%{_unitdir}/%{name}.service
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}@.service  %{buildroot}%{_unitdir}/%{name}@.service
%{__install} -Dpm 0644 %{buildroot}%{_docdir}/%{name}/stellar-core_example.cfg %{buildroot}%{_sysconfdir}/stellar/%{name}.cfg

%{__install} -d %{buildroot}/var/log/stellar
%{__install} -d %{buildroot}/var/lib/stellar/core
%{__install} -d %{buildroot}%{_sysconfdir}/stellar

%if 0%{?el7}
    %{__install} -D /opt/rh/rh-postgresql13/root/usr/lib64/libpq.so.rh-postgresql13-5 %{buildroot}%{_datadir}/%{system_name}/lib/libpq.so.rh-postgresql13-5
%endif

%check
%if 0%{?el7}
# ./xdrc/xdrc -hh -o tests/xdrtest.hh tests/xdrtest.x
# g++: error: unrecognized command line option '-std=c++17'
source /opt/rh/rh-postgresql13/enable
source /opt/rh/llvm-toolset-14.0/enable
%endif

make check

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
%if 0%{?el7}
    %{_datadir}/%{system_name}/lib/libpq.so.rh-postgresql13-5
%endif

%changelog
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
