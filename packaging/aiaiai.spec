Name:       aiaiai
Summary:    Kernel patch validation scripts
Version:    1.2
Release:    1
Group:      Development/Tools/Other
License:    GPLv2
URL:        http://git.nifradead.org/users/dedekind/aiaiai.git

Source0:    %{name}-%{version}.tar.bz2

Requires:   python >= 2.5
Requires:   perl
Requires:   git-core
Requires:   gcc
Requires:   make
Requires:   cppcheck
Requires:   smatch
Requires:   sparse
Requires:   coccinelle
Requires:   /usr/bin/lockfile
Requires:   /usr/bin/formail
Requires:   /bin/sed
Requires:   /bin/grep
Requires:   /bin/awk
Requires:   /usr/bin/diff

%description
Set of scripts and tools for verifying Linux kernel patches.

%package email
Summary:    Kernel patch validation scripts (email handling part)
Group:      Development/Tools/Other

Requires:   %name = %{version}-%{release}
Requires:   /usr/bin/inotifywait
Requires:   mutt

%description email
All the scripts related to emails handling. If you use Aiaiai locally
you do not need these scripts.

%prep
%setup -q -n %{name}-%{version}

%build
make %{?_smp_mflags}

%install
install -d %{buildroot}/usr/bin
cp -a * %{buildroot}/usr/bin
rm -rf %{buildroot}/usr/bin/packaging
rm -rf %{buildroot}/usr/bin/doc
rm %{buildroot}/usr/bin/*.c
rm %{buildroot}/usr/bin/Makefile
rm %{buildroot}/usr/bin/helpers/*.c
rm %{buildroot}/usr/bin/helpers/Makefile

%files
%defattr(-,root,root,-)
%{_bindir}/aiaiai*
%{_bindir}/helpers

%files email
%defattr(-,root,root,-)
%{_bindir}/email/*

%doc doc/README doc/README.announcement
