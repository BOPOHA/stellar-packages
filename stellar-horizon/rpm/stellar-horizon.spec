%global debug_package %{nil}

Name: stellar-horizon
Version: 29.0.0
Release: 1%{?dist}
Summary: Client-facing API server for the Stellar network

License: Apache 2.0
Source0: {{{ git_dir_pack }}}
Source1: https://github.com/stellar/stellar-horizon/archive/refs/tags/v%{version}.tar.gz#/stellar-horizon-v%{version}.tar.gz

Requires: user(stellar)
Requires: group(stellar)

BuildRequires: git >= 2.0
BuildRequires: golang >= 1.25
BuildRequires: systemd-rpm-macros
%if 0%{?rhel} && 0%{?rhel} == 7
BuildRequires: rh-postgresql13-postgresql-server
%else
BuildRequires: postgresql-server >= 13.0
%endif

Provides: %{name} = %{version}

%description
Client-facing API server for the Stellar network. It acts as the interface between Stellar Core and
applications that want to access the Stellar network. It allows you to submit transactions to the network,
check the status of accounts, subscribe to event streams and more.

%prep
{{{ git_dir_setup_macro }}}
%setup -q -b 1 -T -D -n %{name}-%{version}

%build
# Build the versioned standalone Horizon repository. The external linker keeps
# the RPM build-id behavior used by the previous package.
go mod vendor
go build --mod vendor -trimpath -ldflags="-s -w -linkmode=external -X github.com/stellar/go-stellar-sdk/support/app.version=%{version}-%{release}" -o %{name} .

%install
%{__install} -Dpm 0755 %{name} %{buildroot}%{_bindir}/%{name}
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.service   %{buildroot}%{_unitdir}/%{name}.service

%check
%if 0%{?rhel} && 0%{?rhel} == 7
    source /opt/rh/rh-postgresql13/enable
%endif
# Run Horizon's unit suite against an isolated PostgreSQL instance. Integration
# tests are skipped unless explicitly enabled by their upstream environment flag.
export PGDATA=`mktemp -d`
initdb --no-locale -E UTF8 -U postgres
echo -e "logging_collector=off\nlog_min_messages=INFO\nunix_socket_directories='$PGDATA'\n" >> $PGDATA/postgresql.conf
pg_ctl -l $PGDATA/log.txt start
sleep 1
go test -count=1 ./...
pg_ctl stop

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%files
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}

%changelog
* Fri Oct 09 2026 Anatolii Vorona <vorona.tolik@gmail.com>
- update to v29.0.0 from the standalone Horizon repository

* Tue Sep 19 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v2.26.1

* Tue Apr 25 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v2.24.1

* Thu Feb 9 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update Horizon v2.24.0

* Thu Dec 8 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update Horizon v2.23.1

* Tue Nov 1 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update Horizon v2.22.1

* Thu Oct 13 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update Horizon v2.21.0

* Wed Mar 23 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- init stellar-horizon rpm
