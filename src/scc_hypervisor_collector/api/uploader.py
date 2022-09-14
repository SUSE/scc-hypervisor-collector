"""
SCC Hypervisor Collector SCCUploader

The SCCUploader is responsible for uploading the hypervisor details
collected from the specified backends to the SCC using the provided
credentials.
"""
import json
import logging
import gzip
from importlib_metadata import version as get_package_version
import requests
from requests.exceptions import RequestException

from .configuration import SccCredsConfig
from .hypervisor_collector import HypervisorCollector


class SCCUploader:
    """SCC Uploader for scc-hypervisor-collector."""

    def __init__(self, scc_creds: SccCredsConfig,
                 scc_base_url: str = 'https://scc.suse.com'):
        """Initialiser for SCCUploader"""
        self._log = logging.getLogger(__name__)

        # save the parameters
        self._scc_creds = scc_creds
        self.auth = requests.auth.HTTPBasicAuth(self._scc_creds.username,
                                                self._scc_creds.password)

        self.headers = {
            'X-Gatherer-Version':
                get_package_version('virtual-host-gatherer'),
            'X-Scc-Hypervisor-Collector-Version':
                get_package_version('scc-hypervisor-collector'),
            'Content-Type': 'application/json'
        }
        self.scc_base_url = scc_base_url

    def upload(self, hv: HypervisorCollector,
               path: str =
               '/connect/organizations/virtualization_hosts') -> None:
        """ Upload the collected details to SCC"""
        headers = self.headers
        headers.update({'Content-Encoding': 'gzip'})
        zipped_payload = gzip.compress(json.dumps(hv.details).encode('utf-8'))

        try:
            response = requests.put(self.scc_base_url + path,
                                    auth=self.auth,
                                    headers=headers,
                                    data=zipped_payload,
                                    allow_redirects=False)

            if response.status_code == 200:
                self._log.info("Successfully Uploaded details to SCC for %s",
                               hv.backend)
            else:
                self._log.error("Failed to Upload details to SCC for %s",
                                hv.backend)
                if response.status_code == 429:
                    # TODO(mbelur): retry again
                    pass
        except RequestException:
            error_msg = "upload to scc failed "
            self._log.error(error_msg)

    def check_creds(self,
                    path: str =
                    '/connect/organizations/repositories') -> bool:
        """
        Return True if the GET call to the path is successful
        """
        response = requests.get(self.scc_base_url + path,
                                auth=self.auth,
                                headers=self.headers,
                                allow_redirects=False)
        return response.status_code == 200
