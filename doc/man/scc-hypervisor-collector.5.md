---
title: SCC-HYPERVISOR-COLLECTOR
section: 5
header: SCC Hypervisor Collector Configuration
date: June 2022
---
# NAME

**scc-hypervisor-collector** - SUSE Customer Center hypervisor
collector configuration files.


# DESCRIPTION

The **scc-hypervisor-collector(1)** tool depends upon configuration
settings that specify the hypervisors that it needs to query and the
credientials that it will use to upload the collected details to the
SUSE Customer Center.


# CONFIGURATION FILES

By default the **scc-hypervisor-collector(1)** will check for
configuration files in the **~/.config/scc-hypervisor-collector**
directory of the non-root user account that is running the command.

Only YAML files, with a **.yaml** or **.yml** suffix, will be processed,
and sub-directories will not be traversed.

The **--config-dir** option can be used to specify a different directory,
and the **--config** option can be used to specify an explicit config
file. If both options are specified then the specified config file
contents will be merged over any settings loaded from the specfied
configuration directory.


# ACCESS AND OWNERSHIP

For security reasons only the non-root user that is running the
**scc-hypervisor-collector** command should be able to access the
specified configuration files.


# CONFIGURATION OVERVIEW

The configuration settings must be specified in YAML format, and must
contain the following top level entries:

**credentials**
  : A collection of credentials that will be used by the tool.

**backends**
  : A list of hypervisors that should be queried to obtain the relevant
    details. NOTE: Not required with **--input** is specified.

## CREDENTIALS

The **credentials** collection must contain an **scc** entry, which
in turn must contain the **username** and **password** that will be
used to upload the collected details to the SUSE Customer Center.

## BACKENDS

The **backends** entry is a list of collections of the settings that
are needed to successfully connect to the specified hypervisor in
order to retrieve the required details.

Each entry must contain the following:

**id**
  : Specifies the logical name that will be used to identify the
    associated hypervisor.

**module**
  : The type of the hypervisor. Currently one of 'VMWare', 'Libvirt'.

The other settings that must be specified are dependent upon the type
of hypervisor being queried, and can be seen by running
**virtual-host-gatherer --list**.

## VMWARE (VCENTER) HYPERVISOR SETTINGS

The 'VMware' **module** type can be used to retrieve the relevant
details from VMWare vCenter solutions and requires the following
additional settings:

**hostname**
  : The hostname of the VMWare vCenter to connect to. Note that if
    an IP Adress is specified, it must also be included in any
    associated TLS Certificate if using a secured connection.

**port** (optional)
  : The network port to connect to. Defaults to 443 (HTTPS).

**username**
  : The username to be used for authentication purposes.

**password**
  : The password to be used for authentication purposes.

## LIBVIRT HYPERVISOR SETTINGS

The 'Libvirt' **module** type can be used to retrieve the relevant
details from Libvirt (QEMU/KVM) hypervisors and requires the
following settings:

**uri**
  : Specifies the URI to be used to connect to the target Libvirt
    hypervisor.

**sasl_username** (optional)
  : The SASL Username to be used for SASL authentication.

**sasl_password** (optional)
  : The SASL Password to be used for SASL authentication.

Refer to the **SUSE Virtualization Guide** -> **Managing Virtual
Machines with Libvirt** -> **Connecting and Authorizing**
documentation associated with your SUSE Linux Enterprise Server
release for specific details about configuring remote connection
types.

### Supported Libvirt URIs

While **xen** connection URIs may work, the primary focus for
development and testing has been on **qemu** (QEMU/KVM) Libvirt
hypervisor nodes:

**qemu+ssh**
: This connection type requires that you have setup appropriate
  SSH keys (**ssh-keygen(1)**) that permit passwordless SSH
  connection to the target systems, and that the target user
  account has the required privileges to be able to query the
  relevant details using read-only type requests.

**qemu+tls**
: This connection type requires that you have setup x509 client
  and server certs appropriately on both the target hypervisor
  host and the system on which **scc-hypervisor-collector** will
  be running. See the Virtualization Guide for your SUSE Linux
  Enterprise Server release for more details.


# EXAMPLE CONFIGURATION

```
---

credentials:
  scc:
    username: 'SCC_USERNAME'
    password: 'SCC_PASSWORD'

backends:
  - id: 'vcenter1'
    module: 'VMware'
    hostname: 'dc1-vcenter.example.com'
    port: 443
    username: 'VC1_USERNAME'
    password: 'VC1_PASSWORD'

  - id: 'kvmhost1'
    module: 'Libvirt'
    uri: 'qemu+ssh://someuser@kvmhost1.example.com/system'
```


# AUTHORS

Originally developed by Fergal Mc Carthy (fmccarthy@suse.com) and
Meera Belur (mbelur@suse.com) for the SCC at SUSE LLC (scc-feedback@suse.de)


# LINKS

USE Customer Center: https://scc.suse.com

scc-hypervisor-collector on GitHub: https://github.com/SUSE/scc-hypervisor-collector

virtual-host-gatherer on GitHub: https://github.com/uyuni-project/virtual-host-gatherer

YAML Specification: https://yaml.org/


# SEE ALSO

**scc-hypervisor-collector(1)**, **virtual-host-gatherer(1)**, **ssh(1),
**ssh-keygen(1)**
