import pytest

class TestSCCHypervisorCollectorCLI:
    """Class for scc-hypervisor-collector cli tests"""
    def test_no_arguments(self, capsys, monkeypatch, scc_hypervisor_collector_cli):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        out, err = capsys.readouterr()
        assert "ERROR: No config files found!: config_file='scchvc.yaml'" in err

    def test_bad_option(self, capsys, monkeypatch, scc_hypervisor_collector_cli):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--bad"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        out, err = capsys.readouterr()
        assert "scc-hypervisor-collector: error: unrecognized arguments: --bad\n" in err

    def test_version_option(self, capsys, monkeypatch, scc_hypervisor_collector_cli):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--version"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        out, err = capsys.readouterr()
        assert scc_hypervisor_collector_cli.cli_version in out

    def test_help_option(self, capsys, monkeypatch, scc_hypervisor_collector_cli):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--help"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        out, err = capsys.readouterr()
        assert "usage: scc-hypervisor-collector " in out

    def test_check_option_success(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--check", "--config", "tests/unit/data/config/default/default.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        for record in caplog.records:
            assert record.levelname != 'DEBUG' #default log level is INFO

    def test_check_option_failure(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--check", "--config-dir", "tests/unit/data/config/invalid"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        for record in caplog.records:
            assert record.levelname != 'DEBUG' #default log level is INFO

    def test_quiet_option(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--quiet", "--config", "tests/unit/data/config/default/default.yaml"])
        scc_hypervisor_collector_cli.main()
        for record in caplog.records:
            assert record.levelname != 'DEBUG'
        assert 'query failed after 3 attempts' in caplog.text
        for record in caplog.records:
            if 'query failed after 3 attempts' in record.getMessage():
                assert record.levelname == 'ERROR'

    def test_verbose_option(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--verbose", "--config", "tests/unit/data/config/default/default.yaml"])
        scc_hypervisor_collector_cli.main()
        assert 'query failed after 3 attempts' in caplog.text
        assert 'Lexically sorted config directory files list: ' in caplog.text
        for record in caplog.records:
            if 'query failed after 3 attempts' in record.getMessage():
                assert record.levelname == 'ERROR'
            if 'Lexically sorted config directory files list: ' in record.getMessage():
                assert record.levelname == 'DEBUG'

    def test_verbose_sensitive_field(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--verbose", "--config", "tests/unit/data/config/mock/config.yaml"])
        scc_hypervisor_collector_cli.main()
        assert "3tjdla3gEP4WqkPd" not in caplog.text

    def test_sensitive_field(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector","--config", "tests/unit/data/config/mock/config.yaml"])
        scc_hypervisor_collector_cli.main()
        assert "3tjdla3gEP4WqkPd" not in caplog.text

    def test_logfile(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--logfile", "/tmp/test.log", "--config", "tests/unit/data/config/mock/config.yaml"])
        scc_hypervisor_collector_cli.main()

    def test_invaliddata(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--config-dir", "tests/unit/data/config/invalid"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        assert "Invalid configuration data provided: {'username': 'invalid_scc_username'}" in caplog.text

    def test_requiredfield_libvirt(self, capsys, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--config", "tests/unit/data/config/negative/nourilibvirtbackend.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        out, err = capsys.readouterr()
        assert "ERROR: Invalid configuration data provided" in err

    def test_requiredfield_libvirt_checkmode(self, capsys, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--check", "--config", "tests/unit/data/config/negative/nourilibvirtbackend.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        out, err = capsys.readouterr()
        assert "Invalid backend 'default_libvirt_1' - missing required field: {'uri'}" in out

    def test_check_invalid_backends(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--check", "--config",
                                         "tests/unit/data/config/negative/nobackends.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        assert "Invalid backends section" in caplog.text
        assert "No backends specified in config!" in caplog.text

    def test_invalid_backends(self, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--config",
                                         "tests/unit/data/config/negative/nobackends.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        assert "No backends specified in config!" in caplog.text

    def test_scc_credentials_check_option(self, capsys, monkeypatch, scc_hypervisor_collector_cli):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--scc-credentials-check",  "--config", "tests/unit/data/config/mock/config.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        out, err = capsys.readouterr()
        assert "SCC Credentials Check Verification Failed\n" in out
