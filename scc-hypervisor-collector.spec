#
# spec file for package scc-hypervisor-collector
#
# Copyright (c) 2022 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%define shcuser scchvc
%define skip_python2 1
%global __python %{_bindir}/python3

%{?!python_module:%define python_module() python3-%{**}}
%{?!python_build:%define python_build %{expand:%py3_build}}
%{?!python_install:%define python_install %{expand:%py3_install}}

Name:           scc-hypervisor-collector
Version:        0.0.2~git18.e27f17d
Release:        0
Summary:        Regularly collect and upload hypervisor details to SUSE Customer Care
License:        Apache-2.0
Group:          System/Management
URL:            https://github.com/SUSE/scc-hypervisor-collector
Source0:        scc-hypervisor-collector-%{version}.tar.xz
Source1:        scc-hypervisor-collector.service
Source2:        scc-hypervisor-collector.timer
BuildRequires:  %{python_module importlib-metadata}
BuildRequires:  %{python_module PyYAML}
BuildRequires:  %{python_module requests}
BuildRequires:  %{python_module devel}
BuildRequires:  %{python_module mock}
BuildRequires:  %{python_module pytest}
BuildRequires:  fdupes
BuildRequires:  python-rpm-macros
BuildRequires:  virtual-host-gatherer-Libvirt
BuildRequires:  virtual-host-gatherer-VMware
Requires:       %{name}-common
BuildArch:      noarch
%if 0%{?suse_version} < 1530
BuildRequires:  %{python_module setuptools}
%endif

%description
This package contains the systemd timer and service scripts that will
run the scc-hypervisor-collector on a regular basis.

%package common
Summary:        Tool to collect and upload hypervisor details to SUSE Customer Care
Group:          System/Management
Requires:       %{python_module importlib-metadata}
Requires:       %{python_module PyYAML}
Requires:       %{python_module requests}
Requires:       openssh-clients
Requires:       virtual-host-gatherer-Libvirt
Requires:       virtual-host-gatherer-VMware

%description common
This package contains a script to gather information about virtual
machines running on various hypervisors & VM management solutions.

%prep
%setup -q -n scc-hypervisor-collector-%{version}

%build
%python_build

%install
%python_install

mkdir -p %{buildroot}%{_mandir}/man1
install -m 0644 doc/man/%{name}.1 %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_mandir}/man5
install -m 0644 doc/man/%{name}.5 %{buildroot}%{_mandir}/man5/
mkdir -p %{buildroot}%{_mandir}/man8
install -m 0644 doc/man/%{name}.service.8 %{buildroot}%{_mandir}/man8/

# install service related components
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.timer
mkdir -p %{buildroot}%{_sbindir}
ln -s %{_sbindir}/service %{buildroot}%{_sbindir}/rc%{name}

%fdupes %{buildroot}%{python_sitelib}

%check
export PYTHONPATH=%{buildroot}%{python_sitelib}

# ensure example config permissions are correct
chmod -R g-rwx,o-rwx examples
%{buildroot}%{_bindir}/%{name} -h
%{buildroot}%{_bindir}/%{name} --check --config examples/shc_cfg.yaml

# run tests
pytest -vv

%pre
getent group %{shcuser} >/dev/null || groupadd -r %{shcuser}
getent passwd %{shcuser} >/dev/null || useradd -r -g %{shcuser} \
  -d %{_localstatedir}/lib/%{shcuser} \
  -s /sbin/nologin \
  -c "user for %{name}" %{shcuser}
if [ ! -d %{_localstatedir}/lib/%{shcuser} ]; then
  mkdir -m 700 %{_localstatedir}/lib/%{shcuser}
  chown %{shcuser}:%{shcuser} %{_localstatedir}/lib/%{shcuser}
fi

%service_add_pre %{name}.service
%service_add_pre %{name}.timer

%post
%service_add_post %{name}.service
%service_add_post %{name}.timer

%preun
%service_del_preun %{name}.timer
%service_del_preun %{name}.service

%postun
%service_del_postun %{name}.timer
%service_del_postun %{name}.service

%files
%{_sbindir}/rc%{name}
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.timer

%{_mandir}/man8/*

%files common
%{_bindir}/%{name}

%license LICENSE
%doc README.md
%{_mandir}/man1/*
%{_mandir}/man5/*

%dir %{python_sitelib}/scc_hypervisor_collector
%{python_sitelib}/scc_hypervisor_collector/*.py*
%dir %{python_sitelib}/scc_hypervisor_collector/api
%{python_sitelib}/scc_hypervisor_collector/api/*.py*
%dir %{python_sitelib}/scc_hypervisor_collector/cli
%{python_sitelib}/scc_hypervisor_collector/cli/*.py*

%dir %{python_sitelib}/scc_hypervisor_collector/__pycache__
%{python_sitelib}/scc_hypervisor_collector/__pycache__/*.py*
%dir %{python_sitelib}/scc_hypervisor_collector/api/__pycache__
%{python_sitelib}/scc_hypervisor_collector/api/__pycache__/*.py*
%dir %{python_sitelib}/scc_hypervisor_collector/cli/__pycache__
%{python_sitelib}/scc_hypervisor_collector/cli/__pycache__/*.py*
%{python_sitelib}/scc_hypervisor_collector-*.egg-info

%changelog
