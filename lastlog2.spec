# NOTE: lastlog2 (version 2.x) is packaged in util-linux.spec
Summary:	Y2038 safe version of lastlog
Summary(pl.UTF-8):	Wersja usługi lastlog bezpieczna pod kątem Y2038
Name:		lastlog2
Version:	1.3.1
Release:	1.1
License:	BSD
Group:		Libraries
#Source0Download: https://github.com/thkukuk/lastlog2/tags
Source0:	https://github.com/thkukuk/lastlog2/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	2b3534210f9f51406e3c67cdf0f2a309
Patch0:		split-usr.patch
URL:		https://github.com/thkukuk/lastlog2
# _TIME_BITS=64
BuildRequires:	glibc-devel >= 6:2.34
BuildRequires:	libxslt-progs
BuildRequires:	meson >= 0.61.0
BuildRequires:	ninja >= 1.5
BuildRequires:	pam-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.736
BuildRequires:	sqlite3-devel >= 3
Requires:	systemd-units >= 38
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin

%description
The standard /var/log/lastlog implementation using lastlog.h from
glibc uses a 32bit time_t in struct lastlog on bi-arch systems like
x86-64 (so which can execute 64bit and 32bit binaries). So even if you
have a pure 64bit system, on many architectures using glibc you have a
Y2038 problem.

Additional, /var/log/lastlog can become really huge if there are big
UIDs in use on the system. Since it is a sparse file, this is normally
not a problem, but depending on the filesystem or the tools used for
backup, this can become a real problem.

Since there are only few applications which really support lastlog,
the data is also not always correct.

lastlog2 tries to solve this problems:
- It's using sqlite3 as database backend.
- Data is only collected via a PAM module, so that every tools can
  make use of it, without modifying existing packages.
- The output is as compatible as possible with the old lastlog
  implementation.
- The old /var/log/lastlog file can be imported into the new database.
- The size of the database depends on the amount of users, not how big
  the biggest UID is.

%description -l pl.UTF-8
Standardowa implementacja /var/log/lastlog z użyciem lastlog.h z glibc
wykorzystuje 32-bitowy time_t w strukturze lastlog na systemach
wieloarchitekturowych, takich jak x86-64 (który może wykonywać binaria
64- i 32-bitowe). Przez to nawet na czysto 64-bitowym systemie, na
wielu architekturach wykorzystujących glibc można napotkać problem
roku 2038.

Ponadto /var/log/lastlog może stać się bardzo duży, jeśli w systemie
używane są duże UID-y. Ponieważ jest to plik rzadki, zwykle nie jest
to problem, ale może być w zależności od używanego systemu plików i
narzędzi do wykonywania kopii zapasowych.

Ponieważ tylko kilka aplikacji tak naprawdę obsługuje lastlog, dane
nie muszą być zawsze poprawne.

lastlog2 próbuje rozwiązać te problemy:
- wykorzystuje sqlite3 jako backend bazy danych
- dane są zbierane tylko przez moduł PAM, więc wszystkie narzędzia
  mogą go używać bez dodatkowych modyfikacji
- wyjście jest zgodne ze starą implementacją lastlog na ile to możliwe
- stary plik /var/log/lastlog można zaimportować do nowej bazy danych
- rozmiar bazy danych zależy od liczby użytkowników, a nie najwyższej
  wartości UID-a

%package -n pam-pam_lastlog2
Summary:	PAM module to display date of last login
Summary(pl.UTF-8):	Moduł PAM do wyświetlania daty ostatniego logowania
Group:		Base
Requires:	%{name} = %{version}-%{release}

%description -n pam-pam_lastlog2
PAM module to display date of last login.

%description -n pam-pam_lastlog2 -l pl.UTF-8
Moduł PAM do wyświetlania daty ostatniego logowania.

%package devel
Summary:	Header files for lastlog2 library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki lastlog2
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for lastlog2 library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki lastlog2.

%prep
%setup -q
%patch -P0 -p1

%build
%meson \
	--sbindir=%{_sbindir} \
	-Dsplit-usr=true

%meson_build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/lib/lastlog

%meson_install

:> $RPM_BUILD_ROOT/var/lib/lastlog/lastlog2.db

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
%systemd_post lastlog2-import.service

%preun
%systemd_preun lastlog2-import.service

%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE NEWS README.md
%attr(755,root,root) %{_sbindir}/lastlog2
%attr(755,root,root) %{_libdir}/liblastlog2.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/liblastlog2.so.1
%{_mandir}/man8/lastlog2.8*
%{systemdunitdir}/lastlog2-import.service
%{systemdtmpfilesdir}/lastlog2.conf
%dir /var/lib/lastlog
%ghost /var/lib/lastlog/lastlog2.db

%files -n pam-pam_lastlog2
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/security/pam_lastlog2.so
%{_mandir}/man8/pam_lastlog2.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/liblastlog2.so
%{_includedir}/lastlog2.h
%{_pkgconfigdir}/liblastlog2.pc
