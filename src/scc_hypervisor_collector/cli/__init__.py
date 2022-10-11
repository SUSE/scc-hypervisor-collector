""""
SCC Hypervisor Collect CLI Implementation
"""
import argparse
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import (Any, Optional, Sequence, Tuple)
from logging.handlers import RotatingFileHandler
import yaml

from scc_hypervisor_collector import (
    __version__ as cli_version,
    ConfigManager,
    CollectionResults,
    CollectionScheduler,
    SCCUploader,
)
from scc_hypervisor_collector.api import (
    CollectorException
)


class PermissionsRotatingFileHandler(RotatingFileHandler):
    """ RotatingFileHandler with permissions set"""
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        os.chmod(self.baseFilename, 0o0600)


def create_logger(level: str,
                  logfile: Path) -> logging.Logger:
    """Create a logger for use with the scc-hypervisor-collector """
    logger = logging.getLogger()
    logger.setLevel(level)

    fmt_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt_str)
    loghandler: Any = None
    if logfile:
        try:
            loghandler = PermissionsRotatingFileHandler(
                    logfile,
                    maxBytes=(0x100000 * 5),
                    backupCount=5)
        except OSError as error:
            loghandler = logging.StreamHandler()
            if level != 'DEBUG':
                formatter = logging.Formatter('%(levelname)s - %(message)s')
                print("Error:", error, file=sys.stderr)
            else:
                traceback.print_exc()
    else:
        loghandler = logging.StreamHandler()
        if level != 'DEBUG':
            formatter = logging.Formatter('%(levelname)s - %(message)s')

    loghandler.setFormatter(formatter)
    logger.addHandler(loghandler)

    return logger


def printlog(log_level: int, error: Exception, logger: logging.Logger) -> None:
    """ Print log message """
    if isinstance(logger.handlers[0], PermissionsRotatingFileHandler):
        print("ERROR:", error, file=sys.stderr)
        logger.error("ERROR:", exc_info=True)
    else:
        if log_level != logging.DEBUG:
            print("ERROR:", error, file=sys.stderr)
        else:
            logger.error("ERROR:", exc_info=True)


def check_scc_credentials(scc_credentials_check: bool,
                          cfg_mgr: ConfigManager) -> None:
    """
    Validate the SCC credentials supplied when
    --scc-credentials-check is set
    """
    if scc_credentials_check:
        uploader = SCCUploader(cfg_mgr.config_data.credentials.scc)
        if uploader.check_creds():
            print("SCC Credentials Check Verification Successful")
        else:
            print("SCC Credentials Check Verification Failed")
        sys.exit(0)


def upload(cfg_mgr: ConfigManager, collected: CollectionResults,
           logger: logging.Logger, retry: bool) -> None:
    """
        Upload the hypervisor details to SCC
    """
    uploader = SCCUploader(cfg_mgr.config_data.credentials.scc)
    for entry in collected.results:
        if entry.get('valid'):
            logger.info("Uploading details to SCC for %s",
                        entry['backend'])
            uploader.upload(details=entry['details'],
                            backend=entry['backend'],
                            retry=retry)
        else:
            logger.error("Not Uploading details to SCC for %s "
                         "as collection for this backend failed",
                         entry['backend'])


def create_options_parser() -> argparse.ArgumentParser:
    """Create a parser to parse the CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Collect configured hypervisor details and upload to "
                    "SUSE Customer Center (SCC)."
    )

    # General purpose options
    parser.add_argument('-V', '--version', action='version',
                        version="%(prog)s " + str(cli_version))

    # Output verbosity control
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-q', '--quiet', action='store_true',
                           help="Decrease output verbosity.")
    verbosity.add_argument('-v', '--verbose', action='store_true',
                           help="Increase output verbosity.")

    # Primary command line options
    parser.add_argument('-c', '--config', default='scchvc.yaml',
                        help="The YAML config file to use.")
    parser.add_argument('--config_dir', '--config-dir',
                        default='~/.config/scc-hypervisor-collector',
                        help="The config directory to check for YAML "
                             "config files.")
    parser.add_argument('-C', '--check', action='store_true',
                        help="Check the configuration data "
                             "only, reporting any errors.")
    parser.add_argument('-S', '--scc-credentials-check', action='store_true',
                        help="Validate the supplied SCC credentials")
    default_log_destination = f"{os.path.expanduser('~')}/" \
                              f"scc-hypervisor-collector.log"
    parser.add_argument('-L', '--logfile', action='store', type=Path,
                        default=Path(default_log_destination),
                        help="path to logfile. "
                             f"Default: {default_log_destination}")
    parser.add_argument('-u', '--upload', action='store_true',
                        default=False, help="Upload the data collected to SCC")
    parser.add_argument('-r', '--retry-on-rate-limit', '--retry_on_rate_limit',
                        action='store_true', default=False,
                        help="Retry uploading the collected data to "
                             "SCC if rate limit is encountered")
    io_group = parser.add_mutually_exclusive_group()
    io_group.add_argument('-i', '--input', type=Path, action='store',
                          help="File from which previously saved collection "
                               "data should be loaded.")
    io_group.add_argument('-o', '--output', type=Path, action='store',
                          help="File in which to save collection data for "
                               "later reuse.")

    return parser


def setup_logging(args: argparse.Namespace) -> Tuple[logging.Logger, int]:
    """Setup the logging environment and default log_level."""
    if args.quiet:
        log_level = logging.WARN
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = create_logger(
        level=logging.getLevelName(log_level), logfile=args.logfile
    )

    return (logger, log_level)


def fail_if_run_as_root() -> None:
    """Fail if effectively being run as root."""
    # Check for privileges - cannot be run as root
    if os.geteuid() == 0:
        sys.exit('This tool cannot be run as root!')


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Implements CLI for the scc-hypervisor-gatherer."""

    parser = create_options_parser()

    args = parser.parse_args(argv)

    logger, log_level = setup_logging(args)

    fail_if_run_as_root()

    cfg_mgr = ConfigManager(config_file=args.config,
                            config_dir=args.config_dir,
                            check=args.check,
                            backends_required=not args.input)

    try:
        logger.info("ConfigManager: config_data = %s",
                    repr(cfg_mgr.config_data))
    except CollectorException as e:
        printlog(log_level, e, logger)
        sys.exit(1)

    if args.check:
        for error in cfg_mgr.config_data.config_errors:
            print(error)
        sys.exit(0)

    check_scc_credentials(args.scc_credentials_check, cfg_mgr)

    if args.input:
        try:
            collected_results = CollectionResults()
            collected_results.load(args.input)
        except CollectorException as e:
            printlog(log_level, e, logger)
            sys.exit(1)
    else:
        try:
            scheduler = CollectionScheduler(cfg_mgr.config_data)
            logger.debug("Scheduler: scheduler = %s", repr(scheduler))
            scheduler.run()
            collected_results = scheduler.results
        except CollectorException as e:
            printlog(log_level, e, logger)
            sys.exit(1)

    if args.output:
        try:
            collected_results.save(args.output)
        except CollectorException as e:
            printlog(log_level, e, logger)
            sys.exit(1)
    elif args.upload:
        upload(cfg_mgr=cfg_mgr, collected=collected_results, logger=logger,
               retry=args.retry_on_rate_limit)
    else:
        for hv in collected_results.results:
            print(yaml.safe_dump(hv))


__all__ = ['main']
