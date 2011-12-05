%define provider_dir %{_libdir}/cmpi
%define tog_pegasus_version 2:2.5.1

Summary:        SBLIM fsvol instrumentation
Name:           sblim-cmpi-fsvol
Version:        1.5.0
Release:        2%{?dist}
License:        EPL
Group:          Applications/System
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
URL:            http://sourceforge.net/projects/sblim/
Source0:        http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2
Patch1:		sblim-cmpi-fsvol-1.5.0-vda.patch
BuildRequires:  tog-pegasus-devel >= %{tog_pegasus_version}
BuildRequires:  sblim-cmpi-base-devel
Requires:       tog-pegasus >= %{tog_pegasus_version}
Requires:       sblim-cmpi-base
Requires:       /etc/ld.so.conf.d
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
Standards Based Linux Instrumentation Fsvol Providers

%package devel
Summary:        SBLIM Fsvol Instrumentation Header Development Files
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       tog-pegasus

%description devel
SBLIM Base Fsvol Development Package

%package test
Summary:        SBLIM Fsvol Instrumentation Testcases
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
Requires:       sblim-testsuite
Requires:       tog-pegasus

%description test
SBLIM Base Fsvol Testcase Files for SBLIM Testsuite

%prep
%setup -q
%patch1 -p1 -b .vda

%build
%ifarch s390 s390x ppc ppc64
export CFLAGS="$RPM_OPT_FLAGS -fsigned-char"
%else
export CFLAGS="$RPM_OPT_FLAGS" 
%endif
%configure \
        TESTSUITEDIR=%{_datadir}/sblim-testsuite \
        CIMSERVER=pegasus \
        PROVIDERDIR=%{provider_dir}
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
# remove unused libtool files
rm -f $RPM_BUILD_ROOT/%{_libdir}/*a
rm -f $RPM_BUILD_ROOT/%{provider_dir}/*a
# shared libraries
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/cmpi" > $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%files
%defattr(-,root,root,0755)
%{_libdir}/libcmpiOSBase_CommonFsvol*.so.*
%{provider_dir}/libcmpiOSBase_LocalFileSystemProvider.so
%{provider_dir}/libcmpiOSBase_NFSProvider.so
%{provider_dir}/libcmpiOSBase_BlockStorageStatisticalDataProvider.so
%{provider_dir}/libcmpiOSBase_HostedFileSystemProvider.so
%{provider_dir}/libcmpiOSBase_BootOSFromFSProvider.so
%{_datadir}/%{name}
%docdir %{_datadir}/doc/%{name}-%{version}
%{_datadir}/doc/%{name}-%{version}
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%files devel
%defattr(-,root,root,0755)
%{_libdir}/libcmpiOSBase_CommonFsvol*.so
%{_includedir}/sblim/*Fsvol.h

%files test
%defattr(-,root,root,0755)
%{_datadir}/sblim-testsuite/test-cmpi-fsvol.sh
%{_datadir}/sblim-testsuite/cim/*FileSystem.cim
%{_datadir}/sblim-testsuite/cim/*FS.cim
%{_datadir}/sblim-testsuite/cim/*BlockStorageStatisticalData.cim
%{_datadir}/sblim-testsuite/system/linux/*FileSystem.*
%{_datadir}/sblim-testsuite/system/linux/*FileSystemEntries.*

%define FSVOL_SCHEMA %{_datadir}/sblim-cmpi-fsvol/Linux_Fsvol.mof
%define FSVOL_REGISTRATION %{_datadir}/sblim-cmpi-fsvol/Linux_Fsvol.registration

%pre
# If upgrading, deregister old version
if [ $1 -gt 1 ]; then
  %{_datadir}/sblim-cmpi-fsvol/provider-register.sh -d \
  -t pegasus -r %{FSVOL_REGISTRATION} -m %{FSVOL_SCHEMA} > /dev/null 2>&1 || :;
fi

%post
/sbin/ldconfig
if [ $1 -ge 1 ]; then
# Register Schema and Provider - this is higly provider specific
  %{_datadir}/sblim-cmpi-fsvol/provider-register.sh \
  -t pegasus -r %{FSVOL_REGISTRATION} -m %{FSVOL_SCHEMA} > /dev/null 2>&1 || :;
fi;

%preun
# Deregister only if not upgrading 
if [ $1 -eq 0 ]; then
  %{_datadir}/sblim-cmpi-fsvol/provider-register.sh -d \
  -t pegasus -r %{FSVOL_REGISTRATION} -m %{FSVOL_SCHEMA} > /dev/null 2>&1 || :;
fi

%postun -p /sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Mon Jul 26 2010 Radek Vokal <rvokal@redhat.com> - 1.5.0-2
- add KVM/vda support
- Resolves: #616171

* Wed Jun 30 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.5.0-1
- Update to sblim-cmpi-fsvol-1.5.0

* Wed Oct 14 2009 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.4.4-1
- Initial support
