"""
SCC Hypervisor Collector HypervisorCollector.

The HypervisorCollector can be used to retrieve the Hypervisor and VM
details from a hypervisor backend specified by the user provided
configuration data. It takes a BackendConfig as input.

A hypervisor backend can, potentially, be any one of those supported
by the uyuni/virtual-host-gatherer project, though our primary focus
will be on the "VMware" and "Libvirt" backend support.

Other potential backends, at the time of writing this, are:
  * AmazonEC2
  * Azure
  * GoogleGCE
  * Kubernetes
  * NutanixAHV
"""

import logging
from typing import (cast, Dict, Optional, Sequence)

from .configuration import BackendConfig


class HypervisorCollector:
    """Hypervisor Collector for scc-hypervisor-collector

    The HypervisorCollector manages the collection of backend details
    using the virtual-host-gatherer to perform the query.

    Arguments:
        backend (BackendConfig): the backend config to be managed
            by this HypervisorCollector instance.

        retries (int, default 3): the max number of retries to be
            attempted when querying the backend hypervisor before
            raising a HypervisorCollectorRetriesExhausted exception.

    Special Methods:
        run(): runs the backend query if not already run, retrying
            up to the specified max retries if needed.

    Special Properties:
        backend (BackendConfig): the backend specified as argument
            when the HypervisorCollector was instantiated.

        results (Dict): the results from querying the specified
            backend using the virtual-host-gatherer.

        hosts (List): the list of hypervisor hosts for which entries
            can be found in the results.

        details (Dict): summary details extracted from the results.

        pending (bool): indicates if the collection of results still pending

        succeeded (bool): indicates if the results have been successfully
            collected

        failed (bool): indicates if the results collection had a failure
    """

    def __init__(self, backend: BackendConfig, retries: int = 3):
        """Initialiser for HypervisorCollector"""
        self._log = logging.getLogger(__name__)

        self._log.debug("backend=%s, retries=%d", repr(backend), retries)

        # save the parameters
        self._backend: BackendConfig = backend

        # ensure queries will be retried at least once, even if retries <= 0
        self._retries: int = max(retries, 1)

        # Lazy loaded attributes
        self._results: Optional[Dict] = None
        self._details: Optional[Dict] = None

        self._status = 'pending'

    @property
    def backend(self) -> BackendConfig:
        """Return the associated backend config."""
        return self._backend

    @property
    def retries(self) -> int:
        """Return the specified retry count."""
        return self._retries

    def _worker_run(self) -> Optional[Dict]:
        """Return results or running worker.run()"""
        return self.backend.worker.run()

    def _query_backend(self) -> Dict:
        """Query the specified backend to obtained required data.

        Returns:
            Dict: The dictionary of retrieved data.
        """
        # specify the backend settings to use when running the query.
        self.backend.worker.set_node(self.backend)

        # retry for at most specified retry count, breaking out if
        # non-empty results returned for specified backend.
        attempt = 0
        while attempt < self.retries:
            attempt += 1

            # results are a dictionary on success or None if an error
            # occurred, such as a connection failure/network timeout
            results: Optional[Dict] = self._worker_run()

            # If we got a valid result for the backend then break out
            # of the retry loop.
            if results is not None:
                self._status = 'success'
                break

            self._log.debug("Backend %s, module %s, attempt %d failed",
                            repr(self.backend.id), repr(self.backend.module),
                            attempt)

        else:
            self._status = 'failure'
            results = {}
            self._log.error("Backend %s, module %s, query failed after "
                            "%d attempts", repr(self.backend.id),
                            repr(self.backend.module), attempt)
        if self.succeeded:
            self._log.info("Backend %s, module %s, query succeeded after "
                           "%d attempts", repr(self.backend.id),
                           repr(self.backend.module), attempt)

        return results

    def run(self) -> None:
        """Run the backend query if not already run."""
        if self._results is None and self.pending:
            # Run the backend query
            self._results = self._query_backend()

    @property
    def results(self) -> Dict:
        """Report the collect results, triggering a run if needed."""
        # Run the query if needed
        self.run()

        return cast(Dict, self._results)

    @property
    def hosts(self) -> Sequence[str]:
        """The hypervisor hosts found in the specified backend."""
        return list(self.results.keys())

    @property
    def details(self) -> Dict:
        """Details about the hypervisor and it's VMs."""
        if self._details is None:
            self._details = {
                "virtual_hosts": [{
                    "uuid": i['hostIdentifier'],
                    "properties": {
                        "name": i['name'],
                        "arch": i['cpuArch'],
                        # cast these values as integers with int()
                        # to avoid issues seem when trying to
                        # yaml.safe_dump() them for VMware backends.
                        "sockets": int(i['totalCpuSockets']),
                        "cores": int(i['totalCpuCores']),
                        "threads": int(i['totalCpuThreads']),
                        "ram_mb": i.get('ramMb'),
                        "type": i['type'],
                        "group": self.backend.id
                    },
                    "systems": [{
                        "uuid": u,
                        "properties": {
                            "vm_name": v,
                            "data": dict(tuple(i['optionalVmData'][v].items()))
                        }
                    } for v, u in i['vms'].items()],
                } for h, i in self.results.items()]
            }

        return cast(Dict, self._details)

    @property
    def pending(self) -> bool:
        """Return True if the backend status is pending"""
        return self._status == "pending"

    @property
    def succeeded(self) -> bool:
        """Return True if the backend status is success"""
        return self._status == "success"

    @property
    def failed(self) -> bool:
        """Return True if the backend status is failure"""
        return self._status == "failure"
