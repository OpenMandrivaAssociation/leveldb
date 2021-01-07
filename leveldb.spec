%define major   1
%define libname %mklibname leveldb %{major}
%define devname %mklibname -d leveldb
%define staticname %mklibname -d -s leveldb

Name:           leveldb
Version:        1.22
Release:        1
Summary:        A fast and lightweight key/value database library by Google
Group:          Databases
License:        BSD
URL:            http://github.com/google/leveldb
Source0:        https://github.com/google/leveldb/archive/%{version}.tar.gz
# available in https://github.com/fusesource/leveldbjni/blob/leveldb.patch
Patch0001:	https://src.fedoraproject.org/rpms/leveldb/raw/master/f/0001-Allow-leveldbjni-build.patch
# https://github.com/fusesource/leveldbjni/issues/34
# https://code.google.com/p/leveldb/issues/detail?id=184
# Add DB::SuspendCompactions() and DB:: ResumeCompactions() methods
Patch0002:	https://src.fedoraproject.org/rpms/leveldb/raw/master/f/0002-Added-a-DB-SuspendCompations-and-DB-ResumeCompaction.patch
# Cherry-picked from Basho's fork
Patch0003:	https://src.fedoraproject.org/rpms/leveldb/raw/master/f/0003-allow-Get-calls-to-avoid-copies-into-std-string.patch
# https://groups.google.com/d/topic/leveldb/SbVPvl4j4vU/discussion
Patch0004:	https://src.fedoraproject.org/rpms/leveldb/raw/master/f/0004-bloom_test-failure-on-big-endian-archs.patch
Patch0005:	https://src.fedoraproject.org/rpms/leveldb/raw/master/f/0005-Restore-soname-versioning-with-CMake-build.patch
# memenv is just a static helper lib linked into leveldb these days
Obsoletes:	%mklibname memenv 1

BuildRequires:  snappy-devel
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	pkgconfig(sqlite3)

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
Obsoletes:	%{staticname}

%description -n	%{devname}
Additional header files for development with %{name}.

%prep
%autosetup -p1
%cmake -G Ninja

%build
%ninja_build -C build

%install
%ninja_install -C build

# make pc file
mkdir -p %{buildroot}%{_libdir}/pkgconfig
cat >%{buildroot}%{_libdir}/pkgconfig/%{name}.pc <<"EOF"
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
ctest

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{major}*

%files -n %{devname}
%doc doc/ AUTHORS LICENSE
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/cmake/leveldb
