---
title: SCC-HYPERVISOR-COLLECTOR
section: 1
header: SCC Hypervisor Collector
date: June 2022
---
# NAME
**scc-hypervisor-collector** - Collect & Upload Hypervisor details
to SUSE Customer Center


# SYNOPSIS

**scc-hypervisor-collector [<optional>...]**


# DESCRIPTION

The **scc-hypervisor-collector(1)** collects details relevant to
subscription compliance tracking from customer hypervisor solutions
and uploads them to the SUSE Customer Center (SCC), using provided
customer credentials.


# COLLECTED DETAILS

For each hypervisor node that is managed by the specified hypervisors,
the following details are collected:

**Hypervisor Node Name**
: The name assigned to the hypervisor node

**Hypervisor Node ID**
: The id assigned to the hypervisor node

**Hypervisor Type**
: The id assigned to the hypervisor node

**RAM**
: Total system memory

**CPU Architecture**
: The type of CPU, e.g. **x86_64**, **aarch64**

**CPU Topology**
: The number of sockets, cores and threads

**Hosted VMs**
: List of hosted VM with identification and state info.

For each hosted VM the following details are collected:

**Name**
: The hypervisor configuration name for to the VM

**UUID**
: The UUID associated with the VM if has been registered with the SCC.
  In some cases (VMWare, see below) it may be a mangled form of the
  origial UUID assigned by the hypervisor node.

**VMWare UUID** (VMWare Hypervisors only)
: The UUID that VMWare assigned to the VM.
  Depending on the VMWare hypervisor host software version, the VM
  BIOS version used, and the Linux distribution/release being run,
  in some cases the system UUID reported within the running instance
  may reverse the byte order within each of the first 3 elements of
  the UUID.

**VM State**
: The state of the VM, i.e. running or stopped/shutoff.

## EXAMPLES OF COLLECTED DETAILS

The following examples are YAML representations of the details that
are collected from a QEMU/KVM Libvirt host and a VMWare vCenter:

```
- backend: libvirt0
  details:
    virtualization_hosts:
    - group_name: libvirt0
      identifier: 0dc1c04b-8b98-409c-9f73-45834fca4c73
      properties:
        arch: x86_64
        cores: 12
        name: libvirt0.example.com
        ram_mb: 262108
        sockets: 2
        threads: 24
        type: QEMU
      systems:
      - properties:
          vmState: x86_64
          vm_name: vm_libvirt0_0
        uuid: 17ada641-0840-4dec-8b7f-836f36639cef
      - properties:
          vmState: x86_64
          vm_name: vm_libvirt0_1
        uuid: c12f117e-f38a-4722-8e78-5d8524b239d2
      - properties:
          vmState: x86_64
          vm_name: vm_libvirt0_2
        uuid: 7ecf5159-7d7d-4e86-a8e9-b5916ad72a8e
      - properties:
          vmState: x86_64
          vm_name: vm_libvirt0_3
        uuid: 5a6ff93c-1ef7-49f6-99f0-22adc0b1588e
  valid: true

- backend: vcenter0
  details:
    virtualization_hosts:
    - group_name: vcenter0
      identifier: '''vim.HostSystem:host-0'''
      properties:
        arch: x86_64
        cores: 12
        name: esx0.vcenter0.example.com
        ram_mb: 262108
        sockets: 2
        threads: 24
        type: vmware
      systems:
      - properties:
          vmState: x86_64
          vm_name: vm_vcenter0_0_0
          vmware_uuid: c675afea-75db-984b-82cf-fa57b384cfd9
        uuid: eaaf75c6-db75-4b98-82cf-fa57b384cfd9
      - properties:
          vmState: x86_64
          vm_name: vm_vcenter0_0_1
          vmware_uuid: a932fe0e-5d69-e544-9706-d3db67f834fe
        uuid: 0efe32a9-695d-44e5-9706-d3db67f834fe
      - properties:
          vmState: x86_64
          vm_name: vm_vcenter0_0_2
          vmware_uuid: 221e4ab5-1ab5-f248-bf2e-02c6266336e4
        uuid: b54a1e22-b51a-48f2-bf2e-02c6266336e4
      - properties:
          vmState: x86_64
          vm_name: vm_vcenter0_0_3
          vmware_uuid: 26399028-5f3a-9f4c-803a-0353c99eb805
        uuid: 28903926-3a5f-4c9f-803a-0353c99eb805
    - group_name: vcenter0
      identifier: '''vim.HostSystem:host-1'''
      properties:
        arch: x86_64
        cores: 12
        name: esx1.vcenter0.example.com
        ram_mb: 262108
        sockets: 2
        threads: 24
        type: vmware
      systems:
      - properties:
          vmState: x86_64
          vm_name: vm_vcenter0_1_0
          vmware_uuid: 1283147e-b217-1947-b35c-b5eb7676826b
        uuid: 7e148312-17b2-4719-b35c-b5eb7676826b
      - properties:
          vmState: x86_64
          vm_name: vm_vcenter0_1_1
          vmware_uuid: ed340382-28a9-a449-85a0-df6ade7828d9
        uuid: 820334ed-a928-49a4-85a0-df6ade7828d9
      - properties:
          vmState: x86_64
          vm_name: vm_vcenter0_1_2
          vmware_uuid: 4da580e7-fd16-6545-8409-ec1adbd03f26
        uuid: e780a54d-16fd-4565-8409-ec1adbd03f26
      - properties:
          vmState: x86_64
          vm_name: vm_vcenter0_1_3
          vmware_uuid: 5ccd2fd8-933f-4945-80a5-aaec26f6300a
        uuid: d82fcd5c-3f93-4549-80a5-aaec26f6300a
  valid: true
```


# OPTIONS

  **-c**, **--config** **<CONFIG_FILE>**
  : Specifies a file containing YAML configuration settings. If both
    **--config** and **-config-dir** options are specified, the
    specified **--config** file contents will be merged over the
    settings loaded from the **-config-dir** directory, superceding
    any existing settings.

  **--config-dir**, **--config_dir** **<CONFIG_DIR>**
  : Specifies a directory containing one of more YAML configuration
    files, with **.yaml** or **.yml** suffixes that will be merged
    together, in lexical sort order, to construct the configuration
    settings. Note that sub-directories will not be traversed.
    Defaults to **~/.config/scc-hypervisor-collector**.

  **-C**, **--check**
  : Checks the specified configuration settings for correctness, reporting
    any issues found.

  **--scc-credentials-check**
  : Validate that the supplied SCC credentials can be used to successfully
    connect to the SUSE Customer Center.

  **-h**, **--help**
  : Provides basic details about the available command line options.

  **-q**, **--quiet**
  : Runs in quiet mode, only reporting errors.

  **-v**, **--verbose**
  : Runs in verbose mode, reporting additional details.

  **-V**, **--version**
  : Reports the version of **scc-hypervisor-collector**.

  **-L**, **--logfile** **<LOG_FILE>**
  : Specifies the path to the log file in which to write log messages.
    Defaults to **~/scc-hypervisor-collector.log**.

  **-r**, **--retry-on-rate-limit**, **--retry_on_rate_limit**
  : Enable retrying of data upload to the SCC if rate limiting is
    encountered.

  **-u**, **--upload**
  : Upload the data collected to the SCC.

  **-o**, **--output** **OUTPUT**
  : Store collected data in specified file rather than uploading it.
    Mutually exclusive with **--input**.

  **-i**, **--input** **INPUT**
  : Load collected data from specified file rather than retrieving
    from hypervisors that may be configured. Mutually exclusive
    with **--output**.


# SECURITY CONSIDERATIONS

The **scc-hypervisor-collector(1)** is intended to be run from a
restricted service account with no special privileges, and will
exit immediately if it detects that it is running with superuser
privileges.

## HYPERVISOR ACCESS CREDENTIALS

Any hypervisor access credentials that are provided for use with
the **scc-hypervisor-collector(1)** should have minimal privileges
sufficent to allow retrieving the required details about the
hypervisor nodes and then VMs running on them.

## CONFIGURATION SETTINGS & LOG FILE PERMISSIONS

As the **scc-hypervisor-collector(5)** configuration settings
will contain sensitive information such as passwords, the command
requires that all specified configuration files and directories
must be owned by the non-root user that is running the command,
with restrictive permissions allowing only that user to access
those files.

Similarly, while every effort has been taken to ensure that no
sensitive data is being written to the log files, to limit
potential exposure of such information the log files must also
be owned by, and only accessible by, the user that is running
the **scc-hypervisor-collector(5)** command.

## TLS/SSL CERTIFICATES

The **virtual-host-gatherer(1)** framework only supports certs
that are registered with the system certificate stores.
See **update-ca-certificates(8)** for details.

## SSH KEYS

For any **Libvirt** hypervisors that are specified with a **qemu+ssh**
type URI, appropriate SSH keys that support passwordless SSH access
to the target hypervisor node, must be available in the **~/.ssh/**
directory.

See **ssh-keygen(1)** for more details on how to generate appropriate
SSH keys if needed, and **ssh(1)** for the appropriate permissions
for the **~/.ssh/** directory and any keys stored there.

## INPUT & OUTPUT FILES

The input files, like the configuration settings, must be owned by the
non-root user, with permissions that permit only that user to access
it, that is running the command. Similarly, the output file will be
created with the same restrictive permissions and ownership.

## COLLECT ON ONE SYSTEM, UPLOAD ON ANOTHER

Collecting the hypervisor details and uploading them to the SCC
in a single command run may not always be possible. For example,
in some customer environments, systems with the necessary access
to collect hypervisor details may not have the internet access
required to upload the collected details to the SCC.

The **--input** and **--output** options are intended to support
such deployment models, as follows:

* on an internal system, with access to the hypervisors, the
  **scc-hypervisor-collector** can be run using the **--output**
  option to create a hypervisor details file.

* the hypervisor details file can be copied to a system with
  internet access, which just needs the SCC credentials to be
  configured, where the **scc-hypervisor-collector** can be
  run, using the **input** option to specify the hypervisor
  details file, to upload the hypervisor details to the SCC.


# CONFIGURATION SETTINGS

Configuration settings are specified in YAML format and must contain:

**backends**
: a list of hypervisor backends from which to retrieve relevant
  details. NOTE: Not required with **--input** is specified.

**credentials**
: a collection of credentials that will be used to upload the
  collected details to the SUSE Customer Center.

See **scc-hypervisor-collector(5)** for details about the possible
configuration settings.

## CONFIGURATION MANAGEMENT

The configuration settings, which must be in YAML format, can be
specified as:

* a single config file via the **--config** option.
* a directory containing a set of YAML files (with **.yaml** or
  **.yml** suffixes) via the **-config-dir** option.

If a configuration directory is specified then any YAML files found
under that directory, not traversing sub-directories, with **.yaml**
or **.yml** suffixes, will be processed in lexical sort order,
merging their contents together.

If a configuration file was specified, it's contents will be processed
last and merged over any existing configuration settings.

This scheme allows for configuration settings to be split up into
multiple files, e.g. credentials can be specified in one file,
and the hypervisor backends in one or more files. Additionally
specific config settings can be overriden by an explicitly
specified config file.

When splitting the hypervisor backend details among multiple files,
the **backends** lists in each file will be merged together to form
a single combined list; exact duplicates will be ignored but partial
duplicates will result in errors.

## ACCESS AND OWNERSHIP

For security reasons only the non-root user that is running the
**scc-hypervisor-collector** command should be able to access the
specified configuration files.

## CONFIGURATION VALIDATION

The **--check** option can be utilised to check if the specified
configuration settings are valid, or will report any errors that
it detected.

## SUPPORTED HYPERVISORS

The following hypervisor types are supported:

* VMWare vCenter (type **VMware**)
* Libvirt (type **Libvirt**)

Each hypervisor type has specific configuration settings that must
be provided to permit the relevant details to be retrieved; these
settings are documented in **scc-hypervisor-collector(5)**.


# EXIT CODES

**scc-hypervisor-collector** sets the following exit codes:

**0**
:  Run completed successfully, or configuration settings
      are valid if check mode (**--check**) was specified.

**1**
:  An error occurred.

# IMPLEMENTATION

**scc-hypervisor-collector(1)** is implemented in Python.
It communicates with the SUSE Customer Center via a RESTful
JSON API over HTTP using TLS encryption.

## HYPERVISOR DETAILS RETRIEVAL

The **gatherer** Python module provided by the **virtual-host-gatherer(1)**
command is used to retrieve the details from the configured hypervisors.


# ENVIRONMENT

**scc-hypervisor-collector(1)** respects the HTTP_PROXY environment
variable.  See https://www.suse.com/support/kb/doc/?id=000017441 for
more details on how to manually configure proxy usage.


# FILES AND DIRECTORIES

**~/.config/scc-hypervisor-collector/**
: Default configuration directory containing YAML configuration files,
  merged together in lexical sort order. Directory and files must be
  owned by, and only accessible by, the user running the
  **scc-hypervisor-collector(5)** command.

**~/scc-hypervisor-collector.log**
: Default log file which will be automatically rotated and compressed
  if it gets too large. Log files must be owned by, and only accessible
  by, the user running the **scc-hypervisor-collector(5)** command.
  Will be created with appropriate permissions if no log file exists.

**~/.ssh/** (optional)
: Directory holding any SSH keys (**ssh-keygen**) needed to access
  **Libvirt** with **qemu+ssh** URIs.


# AUTHORS

Originally developed by Fergal Mc Carthy (fmccarthy@suse.com) and
Meera Belur (mbelur@suse.com) for the SCC at SUSE LLC (scc-feedback@suse.de)


# LINKS

SUSE Customer Center: https://scc.suse.com

scc-hypervisor-collector on GitHub: https://github.com/SUSE/scc-hypervisor-collector

virtual-host-gatherer on GitHub: https://github.com/uyuni-project/virtual-host-gatherer

YAML Specification: https://yaml.org/


# SEE ALSO

**scc-hypervisor-collector(5)**, **scc-hypervisor-collector.service(8)**, **scc-hypervisor-collector.timer(8)**, **virtual-host-gatherer(1)**, **update-ca-certificates(8)**, **systemd(1)**.
