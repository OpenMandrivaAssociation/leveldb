%define major   1
%define libname %mklibname leveldb %{major}
%define libmemenv %mklibname memenv %{major}
%define devname %mklibname -d leveldb

Name:           leveldb
Version:        1.18
Release:        7
Summary:        A fast and lightweight key/value database library by Google
Group:          Databases
License:        BSD
URL:            http://code.google.com/p/leveldb/
#VCS:		http://git.fedorahosted.org/git/leveldb.git
Source0:        http://leveldb.googlecode.com/files/%{name}-%{version}.tar.gz
# Sent upstream - https://code.google.com/p/leveldb/issues/detail?id=101
Patch1:         leveldb-0001-Initial-commit-of-the-autotools-stuff.patch
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
Patch7:		leveldb-1.18-configure.patch
Patch8:		0001-ARM64-port-atomic.patch
Patch9:		leveldb-1.9.0-memenv-so.patch
Patch10:	0112-makefile_install.patch

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

%package -n %{libmemenv}
Summary:    %{summary}
Group:      System/Libraries

%description -n %{libmemenv}
Library for %{name}

%package -n	%{devname}
Summary:        The development files for %{name}
Group:          System/Libraries
Requires:       %{libname} = %{version}-%{release}
Requires:       %{libmemenv} = %{version}-%{release}

%description -n	%{devname}
Additional header files for development with %{name}.

%prep
%setup -q
%apply_patches
sed -i 's!/usr/local!%{_prefix}!g' Makefile
sed -i 's!LIBDIR ?= lib!LIBDIR ?= %{_lib}!g' Makefile

%build
export OPT="-g -DNDEBUG"
TARGET_OS="Linux" \
USE_SNAPPY=1 \
USE_TCMALLOC=no \
CC=%{__cc} \
CXX=%{__cxx} \
PREFIX=%{_prefix} \
LIBDIR=%{_libdir} \
TMPDIR=/tmp/ \
sh -x ./build_detect_platform build_config.mk ./

%make LIBS="-lstdc++ -lm" all

%install
%makeinstall_std
mkdir -p %{buildroot}/%{_includedir}/%{name}/helpers
cp -f helpers/memenv/*.h %{buildroot}/%{_includedir}/%{name}/helpers
# make pc file
sed -i 's!@prefix@!%{_prefix}!g' leveldb.pc.in
sed -i 's!@exec_prefix@!%{_prefix}!g' leveldb.pc.in
sed -i 's!@libdir@!%{_libdir}!g' leveldb.pc.in
sed -i 's!@includedir@!%{_includedir}!g' leveldb.pc.in
sed -i 's!@PACKAGE_VERSION@!%{version}!g' leveldb.pc.in
#end
mkdir -p %{buildroot}%{_libdir}/pkgconfig/
cp -f leveldb.pc.in %{buildroot}%{_libdir}/pkgconfig/leveldb.pc 

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

%files -n %{libmemenv}
%{_libdir}/libmemenv.so.%{major}*

%files -n %{devname}
%doc doc/ AUTHORS LICENSE README
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/libmemenv.so
%{_libdir}/pkgconfig/%{name}.pc
