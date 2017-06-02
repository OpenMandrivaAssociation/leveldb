%define major   1
%define libname %mklibname leveldb %{major}
%define devname %mklibname -d leveldb
%define staticname %mklibname -d -s leveldb

Name:           leveldb
Version:        1.20
Release:        1
Summary:        A fast and lightweight key/value database library by Google
Group:          Databases
License:        BSD
URL:            http://github.com/google/leveldb
Source0:        https://github.com/google/leveldb/archive/v%{version}.tar.gz
# available in https://github.com/fusesource/leveldbjni/blob/leveldb.patch
Patch0001:	https://pkgs.fedoraproject.org/cgit/rpms/leveldb.git/plain/0001-Allow-leveldbjni-build.patch
# https://github.com/fusesource/leveldbjni/issues/34
# https://code.google.com/p/leveldb/issues/detail?id=184
# Add DB::SuspendCompactions() and DB:: ResumeCompactions() methods
Patch0002:	https://pkgs.fedoraproject.org/cgit/rpms/leveldb.git/plain/0002-Added-a-DB-SuspendCompations-and-DB-ResumeCompaction.patch
# Cherry-picked from Basho's fork
Patch0003:	https://pkgs.fedoraproject.org/cgit/rpms/leveldb.git/plain/0003-allow-Get-calls-to-avoid-copies-into-std-string.patch
# https://groups.google.com/d/topic/leveldb/SbVPvl4j4vU/discussion
Patch0004:	https://pkgs.fedoraproject.org/cgit/rpms/leveldb.git/plain/0004-bloom_test-failure-on-big-endian-archs.patch
# Don't try to do SSE on ARM
Patch0005:	leveldb-1.20-no-sse-on-ARM.patch
# memenv is built only as a static library these days
Obsoletes:	%mklibname memenv 1

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

%package -n	%{staticname}
Summary:        Static library file for %{name}
Group:          System/Libraries
Requires:       %{libname} = %{version}-%{release}

%description -n	%{staticname}
The static library for development with %{name}.

%prep
%setup -q
%apply_patches
sed -i 's!/usr/local!%{_prefix}!g' Makefile
sed -i 's!LIBDIR ?= lib!LIBDIR ?= %{_lib}!g' Makefile
sed -i -e 's!AR) -r!AR) r!g' Makefile

%build
export OPT="%{optflags} -DNDEBUG -fno-builtin-memcmp"
export CFLAGS="$OPT"
export CXXFLAGS="$OPT"
export LDFLAGS="$OPT"
export TARGET_OS="Linux"
export USE_SNAPPY=1
export USE_TCMALLOC=no
export CC=%{__cc}
export CXX=%{__cxx}
export PREFIX=%{_prefix}
export LIBDIR=%{_libdir}
export TMPDIR=/tmp/

%make CC=%{__cc} CXX=%{__cxx} all

%install
# Make sure patch backup files don't end up being packaged
# as headers or so
find . -name "*~" |xargs rm -f

mkdir -p %{buildroot}/%{_includedir}/%{name}/helpers/memenv %{buildroot}%{_libdir}/pkgconfig
cp -a out-shared/lib*.so* %{buildroot}%{_libdir}/
cp -a out-static/lib*.a %{buildroot}%{_libdir}/
cp -a include/%{name}/ %{buildroot}%{_includedir}/
cp -f helpers/memenv/*.h %{buildroot}/%{_includedir}/%{name}/helpers
for i in helpers/memenv/*.h; do
	ln -s ../$(basename $i) %{buildroot}%{_includedir}/%{name}/helpers/memenv/
done
# make pc file
cat >%{buildroot}%{_libdir}/pkgconfig/leveldb.pc <<"EOF"
prefix=%{_prefix}
exec_prefix=${prefix}
libdir=%{_libdir}
includedir=%{_includedir}

Name: %{name}
Description: %{summary}
Version: %{version}
Libs: -l%{name}
EOF

%check
%make check

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{major}*

%files -n %{devname}
%doc doc/ AUTHORS LICENSE
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/libmemenv.a

%files -n %{staticname}
%{_libdir}/lib%{name}.a
