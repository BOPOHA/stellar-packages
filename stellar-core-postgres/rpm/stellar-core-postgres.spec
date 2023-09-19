%global debug_package %{nil}

Name: stellar-core-postgres
Version: 19.13.0
Release: 1%{?dist}
Summary: Postgresql configuration for the Stellar Core
License: Apache 2.0
Source0: {{{ git_dir_pack }}}

BuildRequires: systemd-rpm-macros
Requires: stellar-core == %{version}
Requires: postgresql-server

%description
The stellar-core-postgres package contains config files for postgres core db and stellar-core.

%prep
{{{ git_dir_setup_macro }}}

%install
%{__install} -d %{buildroot}%{_libexecdir}/stellar/
%{__install} -d %{buildroot}%{_datadir}/stellar/

%{__install} -Dpm 0644 dist/%{name}-public.cfg            %{buildroot}%{_sysconfdir}/stellar/%{name}-public.cfg
%{__install} -Dpm 0644 dist/unit.postgresql.core.conf     %{buildroot}%{_sysconfdir}/systemd/system/postgresql@core.service.d/custom.conf
%{__install} -Dpm 0644 dist/unit.stellar-core.public.conf %{buildroot}%{_sysconfdir}/systemd/system/stellar-core@public.service.d/custom.conf
%{__install} -Dpm 0644 dist/postgres.*.conf               %{buildroot}%{_datadir}/stellar/
%{__install} -Dpm 0755 dist/libexec.init-db-core.sh       %{buildroot}%{_libexecdir}/stellar/init-db-core
%{__install} -Dpm 0755 dist/libexec.init-stellar-core.sh  %{buildroot}%{_libexecdir}/stellar/init-stellar-core

%files
%config(noreplace) %{_sysconfdir}/stellar/%{name}-public.cfg
%{_sysconfdir}/systemd/system/postgresql@core.service.d/custom.conf
%{_sysconfdir}/systemd/system/stellar-core@public.service.d/custom.conf
%{_datadir}/stellar/postgres.*.conf
%{_libexecdir}/stellar/init-db-core
%{_libexecdir}/stellar/init-stellar-core

%post
%systemd_post postgresql@core.service
%systemd_post stellar-core@public.service

%preun
%systemd_preun stellar-core@public.service
%systemd_preun postgresql@core.service

%postun
%systemd_postun_with_restart stellar-core@public.service

%changelog
* Tue Sep 19 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.13.0

* Tue Apr 25 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.9.0

* Tue Mar 21 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.8.0

* Thu Feb 9 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.7.0

* Tue Dec 6 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.6.0

* Wed Nov 2 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.5.0

* Wed Oct 12 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update v19.4.0

* Thu Aug  4 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- remove logrotate as history cleaner
- remove publishing a history archive

* Sun Apr 10 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- init stellar-core-postgres rpm
