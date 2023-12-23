Summary:	Y2038 safe version of lastlog
Name:		lastlog2
Version:	1.2.0
Release:	1
License:	BSD
Group:		Libraries
Source0:	https://github.com/thkukuk/lastlog2/releases/download/v%{version}/%{name}-%{version}.tar.xz
# Source0-md5:	66bbadb41de2cefb54a12d689d6f3cb0
Patch0:		split-usr.patch
URL:		https://github.com/thkukuk/lastlog2
BuildRequires:	libxslt-progs
BuildRequires:	meson >= 0.50.0
BuildRequires:	ninja >= 1.5
BuildRequires:	pam-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.736
BuildRequires:	sqlite3-devel
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

IMPORTANT To be Y2038 safe on 32bit architectures, the binaries needs
to be build with a 64bit time_t. This should be the standard on 64bit
architectures.

%package -n pam-pam_lastlog2
Summary:	PAM module to display date of last login
Group:		Base
Requires:	%{name} = %{version}-%{release}

%description -n pam-pam_lastlog2
PAM module to display date of last login.

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
%patch0 -p1

%build
%meson build \
	--sbindir=%{_sbindir} \
	-Dsplit-usr=true

%ninja_build -C build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/lib/lastlog

%ninja_install -C build

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
%doc NEWS README.md
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
