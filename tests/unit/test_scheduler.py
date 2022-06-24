import mock
import pytest

from scc_hypervisor_collector.api import exceptions, CredentialsConfig, CollectorConfig, CollectionScheduler, SccCredsConfig, HypervisorCollector
from tests import utils


class TestScheduler:


    def test_scheduler_invalid_config_none(self):
        with pytest.raises(exceptions.SchedulerInvalidConfigError):
            CollectionScheduler(config=None)

    @pytest.mark.config('tests/unit/data/config/mock/config.yaml', None)
    def test_scheduler(self, config_manager):
        backends = config_manager.config_data.backends
        hypervisor_coll_list = []
        for each in backends:
            # with mock.patch('scc_hypervisor_collector.api.HypervisorCollector.results',get_results(each.id)):
            # we are mocking the query_backend instead of the results since
            # validate_mock_data is looking at the HypervisorCollector .details and .hosts property value
            # But the .details and .hosts are based on the .results property, so accessing
            # details and hosts causes the HypervisorCollector .run() method to be called to get the results.
            mfilename = 'tests/unit/data/config/mock/mock_' + each.id + '.json'
            with mock.patch('scc_hypervisor_collector.api.HypervisorCollector._query_backend',
                            return_value=utils.read_mock_data(mfilename)):
                hypervisor_collector = HypervisorCollector(backend=each)
                utils.validate_mock_data(hypervisor_collector, each.id)
                hypervisor_coll_list.append(hypervisor_collector)
        with mock.patch('scc_hypervisor_collector.api.CollectionScheduler.hypervisors', tuple(hypervisor_coll_list)):
            scheduler = CollectionScheduler(config_manager.config_data)
            assert len(scheduler.config.backends) == 3
            assert len(scheduler.config.credentials) == 1
            assert len(scheduler.hypervisor_types) == 2
            assert len(scheduler.hypervisor_groups) == 2
            assert len(scheduler.hypervisor_groups['Libvirt']) == 2
            assert len(scheduler.hypervisor_groups['VMware']) == 1
            assert scheduler.hypervisors == tuple(hypervisor_coll_list)
            for each in scheduler.hypervisors:
                utils.validate_mock_data(each, each.backend.id)
                if each.backend.id == 'libvirt1':
                    assert 'sle15-dev' in str(each.details)
                    assert 'sle15-dev' in each.hosts
                    assert 'sle15-dev' in each.results
                if each.backend.id == 'vcenter1':
                    assert 'esx1.test.net' in str(each.details)
                    assert 'esx2.test.net' in str(each.details)
                    assert 'esx1.test.net' in each.hosts
                    assert 'esx1.test.net' in each.results
