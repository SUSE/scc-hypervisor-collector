""""
SCC Hypervisor Collect CLI Implementation
"""
import argparse
import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from typing import (Any, Optional, Sequence)
import yaml

from scc_hypervisor_collector import __version__ as cli_version
from scc_hypervisor_collector import (ConfigManager, CollectionScheduler)
from scc_hypervisor_collector.api import (
    CollectorException
)


class PermissionsRotatingFileHandler(RotatingFileHandler):
    """ RotatingFileHandler with permissions set"""
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        os.chmod(self.baseFilename, 0o0600)


def create_logger(level: str,
                  logfile: str) -> logging.Logger:
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


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Implements CLI for the scc-hypervisor-gatherer."""
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
    default_log_destination = f"{os.path.expanduser('~')}/" \
                              f"scc-hypervisor-collector.log"
    parser.add_argument('-L', '--logfile', action='store',
                        default=default_log_destination,
                        help="path to logfile. "
                             f"Default: {default_log_destination}")

    args = parser.parse_args(argv)

    if args.quiet:
        log_level = logging.WARN
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = create_logger(
        level=logging.getLevelName(log_level), logfile=args.logfile)

    # Check for privileges - cannot be run as root
    if os.geteuid() == 0:
        sys.exit('This tool cannot be run as root!')

    cfg_mgr = ConfigManager(config_file=args.config,
                            config_dir=args.config_dir,
                            check=args.check)

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

    try:
        scheduler = CollectionScheduler(cfg_mgr.config_data)
        logger.debug("Scheduler: scheduler = %s", repr(scheduler))
        scheduler.run()
    except CollectorException as e:
        printlog(log_level, e, logger)
        sys.exit(1)

    # TODO(rtamalin): Make reporting the results like this optional
    # once the SccUploader is implemented.
    for hv in scheduler.hypervisors:
        print(f"[{hv.backend.id}]")
        print(yaml.safe_dump(hv.details))


__all__ = ['main']
