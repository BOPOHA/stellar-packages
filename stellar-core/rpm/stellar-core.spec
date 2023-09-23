%global debug_package %{nil}
%define system_name stellar

Name: stellar-core
Version: 19.14.0
Release: 1%{?dist}
Summary: Stellar is a decentralized, federated peer-to-peer network

License: Apache 2.0
Source0: {{{ git_dir_pack }}}
Source1: https://github.com/stellar/stellar-core/archive/refs/tags/v%{version}.tar.gz#/stellar-core-v%{version}.tar.gz
# START: submodule sources
Source100: https://api.github.com/repos/chriskohlhoff/asio/tarball/c465349fa5cd91a64bb369f5131ceacab2c0c1c3#/chriskohlhoff-asio-asio-1-28-0-0-gc465349.tar.gz
Source101: https://api.github.com/repos/USCiLab/cereal/tarball/ebef1e929807629befafbb2918ea1a08c7194554#/USCiLab-cereal-v1.3.2-0-gebef1e9.tar.gz
Source102: https://api.github.com/repos/fmtlib/fmt/tarball/a0b8a92e3d1532361c2f7feb63babc5c18d00ef2#/fmtlib-fmt-10.0.0-0-ga0b8a92.tar.gz
Source103: https://api.github.com/repos/stellar/medida/tarball/b5b1c5aa63f624749be36ca5bf9efdcd144044e4#/stellar-medida-b5b1c5a.tar.gz
Source104: https://api.github.com/repos/stellar/libsodium/tarball/71d227cf8e4644393a3322f36050f7afdfddc498#/stellar-libsodium-vs2022-0-g71d227c.tar.gz
Source105: https://api.github.com/repos/gabime/spdlog/tarball/7e635fca68d014934b4af8a1cf874f63989352b7#/gabime-spdlog-v1.12.0-0-g7e635fc.tar.gz
Source106: https://api.github.com/repos/stellar/tracy/tarball/897aec5b062664d2485f4f9a213715d2e527e0ca#/stellar-tracy-v0.6.3-3431-g897aec5.tar.gz
Source107: https://api.github.com/repos/xdrpp/xdrpp/tarball/9fd7ca222bb26337e1443c67b18fbc5019962884#/xdrpp-xdrpp-9fd7ca2.tar.gz
Source108: https://api.github.com/repos/stellar/stellar-xdr/tarball/34241a1eb81a715cc75777ca1ed028ea1456645b#/stellar-stellar-xdr-34241a1.tar.gz

# END: submodule sources
%if 0%{?el7}
BuildRequires: devtoolset-11-gcc-c++
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
git init
git add -N .
# START: submodules setup
tar -zxf  %{SOURCE100} --strip-components 1 -C lib/asio/
tar -zxf  %{SOURCE101} --strip-components 1 -C lib/cereal/
tar -zxf  %{SOURCE102} --strip-components 1 -C lib/fmt/
tar -zxf  %{SOURCE103} --strip-components 1 -C lib/libmedida/
tar -zxf  %{SOURCE104} --strip-components 1 -C lib/libsodium/
tar -zxf  %{SOURCE105} --strip-components 1 -C lib/spdlog/
tar -zxf  %{SOURCE106} --strip-components 1 -C lib/tracy/
tar -zxf  %{SOURCE107} --strip-components 1 -C lib/xdrpp/
tar -zxf  %{SOURCE108} --strip-components 1 -C src/protocol-next/xdr/

# END: submodules setup
%if 0%{?el8}%{?fc38}%{?fc39}%{?fc40}
patch -p0 < %{_builddir}/{{{ git_dir_name }}}/patch-001.patch
%endif

%build
%if 0%{?el7}
    LDFLAGS=-Wl,-rpath,%{_datadir}/%{system_name}/lib/
    source /opt/rh/rh-postgresql13/enable
    source /opt/rh/devtoolset-11/enable
%endif
%set_build_flags
./autogen.sh
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
source /opt/rh/devtoolset-11/enable
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
