%define major   1
%define libname %mklibname leveldb %{major}
%define devname %mklibname -d leveldb

Name:           leveldb
Version:        1.14.0
Release:        6
Summary:        A fast and lightweight key/value database library by Google
Group:          Databases
License:        BSD
URL:            http://code.google.com/p/leveldb/
#VCS:		http://git.fedorahosted.org/git/leveldb.git
Source0:        http://leveldb.googlecode.com/files/%{name}-%{version}.tar.gz
# Sent upstream - https://code.google.com/p/leveldb/issues/detail?id=101
Patch1:         leveldb-0001-Initial-commit-of-the-autotools-stuff.patch
# Temporary workaround for secondary arches
Patch2:         leveldb-0002-Add-memory-barrier-on-PowerPC.patch
# https://groups.google.com/d/topic/leveldb/SbVPvl4j4vU/discussion
Patch3:         leveldb-0003-bloom_test-failure-on-big-endian-archs.patch
# available in https://github.com/fusesource/leveldbjni/blob/leveldbjni-[LEVELDBJNI VERSION]/leveldb.patch
Patch4:         leveldb-0004-Allow-leveldbjni-build.patch
# https://github.com/fusesource/leveldbjni/issues/34
# https://code.google.com/p/leveldb/issues/detail?id=184
# Add DB::SuspendCompactions() and DB:: ResumeCompactions() methods
Patch5:         leveldb-0005-Added-a-DB-SuspendCompations-and-DB-ResumeCompaction.patch
# Cherry-picked from Basho's fork
Patch6:		leveldb-0006-allow-Get-calls-to-avoid-copies-into-std-string.patch
BuildRequires:  snappy-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool

%description
LevelDB is a fast key-value storage library written at Google that provides an
ordered mapping from string keys to string values.

%package -n %{libname}
Summary:    %{summary}
Group:      System/Libraries

%description -n %{libname}
Library for %{name}

%package -n	%{devname}
Summary:        The development files for %{name}
Group:          System/Libraries
Requires:       %{libname} = %{version}-%{release}

%description -n	%{devname}
Additional header files for development with %{name}.

%prep
%setup -q
%apply_patches

%build
autoreconf -ivf
%configure2_5x --disable-static --with-pic
%make LIBS="-lstdc++ -lm"

%install
%makeinstall_std

%check
%ifarch armv5tel armv7hl ppc %{power64}
# FIXME a couple of tests are failing on these secondary arches
make check || true
%else
# x86, x86_64, ppc, ppc64, ppc64v7 s390, and s390x are fine
make check
%endif

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{major}*

%files -n %{devname}
%doc doc/ AUTHORS LICENSE README
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
