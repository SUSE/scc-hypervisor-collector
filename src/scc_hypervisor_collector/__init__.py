"""
SCC Hypervisor Collector tool implemented in Python.

Collect hypervisor details for upload to SUSE Customer Center.
The collected details include the UUID, vCPU topology and RAM
for both the hypervisor itself and the running VMs.

Leverages the https://github.com/uyuni/virtual-host-gather project
to collect details from configured hypervisors and upload them to
the SUSE Customer Center.

# Copyright (c) 2022 SUSE LLC, Inc. All Rights Reserved.

See 'ConfigManager' for details on configuration data setup.
"""

from .api import (ConfigManager, CollectionScheduler, SCCUploader)


__author = 'Fergal Mc Carthy <fmccarthy@suse.com>'
__version__ = '0.0.2'

__all__ = [
    'ConfigManager',
    'CollectionScheduler',
    'SCCUploader'
]
