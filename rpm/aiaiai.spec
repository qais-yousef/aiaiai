Name:       aiaiai
Summary:    Kernel patch validation scripts
Version:    1.1.0
Release:    1
Group:      Development/Tools/Other
License:    Intel Proprietary
URL:        http://git.nifradead.org/users/dedekind/aiaiai.git

Source0:    %{name}-%{version}.tar.bz2

Requires:   libshell
Requires:   python >= 2.5
Requires:   perl-base
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
%make_install

%files
%defattr(-,root,root,-)
%{_bindir}/*

%files email
%defattr(-,root,root,-)
%{_bindir}/email/*
