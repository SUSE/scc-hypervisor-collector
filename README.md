# SCC Hypervisor Collector

![CI](https://github.com/SUSE/scc-hypervisor-collector/actions/workflows/ci-workflow.yml/badge.svg)

The `scc-hypervisor-collector` is a tool that can be used to retrieve basic
details (UUID, vCPU topology, RAM) from configured hypervisor backends, and
upload them to the SUSE Customer Center using the configured credentials.

# Dependencies
The `scc-hypervisor-collector` primarily depends on:
* A supported Python 3 (>=3.6) interpreter
* [uyuni/virtual-host-gatherer](https://github.com/uyuni/virtual-host-gatherer) >= 1.0.23
* [pyyaml](https://pypi.org/project/PyYAML/) >= 6.0

Additionally the man pages generation process depends on the following tools
being available:
* [pandoc](https://hackage.haskell.org/package/pandoc)

# Contributing
This project uses the following tools as part of the development process:
* `tox` to manage testing, including support for multiple Python interpreter
  versions using `pyenv`.
* `bumpversion` to manage version updates.
* `pandoc` to generate man pages from Markdown inputs.
  See [man pages README](doc/man/README.md)

## Helper scripts
In the [bin directory](bin/) a number of helper scripts are provided:
* `create-venv` - creates a venv containing the tools (listed above)
  required to support development.
* `command-wrapper` - a generic command wrapper that can be symlinked
  to a command name, and when invoked via that symlink will look for
  the named command in the venv, or failing that will try and run it
  from the host environment.
* `tox` - a `command-wrapper` symlink that can be used to run `tox`.
* `bumpversion` and `bump2version` - `command-wrapper` symlinks that
   can be used to run the `bumpversion` and `bump2version` commands.
* `tox_dev-wrapper` - a generic command wrapper that can be symlinked
  to a command name, and when invoked via that symlink will look for
  the named command in the `tox` created `.tox/dev` venv, or failing
  that will try and run it from the host environment. If you haven't
  yet created the `.tox/dev` venv it will exit with a message telling
  you to run `bin/tox -e dev` to create the venv.
* `scc-hypervisor-collector` and `virtual-host-gatherer` - `tox_dev-wrapper`
  symlinks that can be used to run the `scc-hypervisor-collector` and
  `virtual-host-gatherer` commands.

NOTE:
* `pandoc` is not available as a helper script and instead should be
  installed via your local package manager.

## Testing
The [tox.ini] file is configured to run the following tests:
* `cli` - a simple test to run `scc-hypervisor-collector --help` to verify
  the command can be run from an installed environment.
* `check` - this test checks the code for compliance with recommended Python
  coding practices using `flake8`, `pylint` and `mypy` (for data typing).
* `py<version>-cover` - run `pytest` with/without coverage checking for
  various potential Python versions; missing Python versions will be
  skipped.

Additional tests are also available to be run:
* `dev` - installs the package's dependencies and then installs the package
  itself in developer mode, allowing you to run the code locally for adhoc
  testing purposes via `bin/scc-hypervisor-collector`.

### Enabling multiple Python version testing with pyenv
If you have [pyenv](https://github.com/pyenv/pyenv) installed you can enable
testing against the various supported Python interpreter versions by running
the following command:

```
% pyenv local 3.6.15 3.7.13 3.8.13 3.9.12 3.10.4
```

Note that this only enables those Python interpreter versions (the latest for
each of the supported Python 3.x streams at the time of writing) for use with
tox driven testing. You will still need to install the relevant versions of
the Python interpreter using `pyenv install <version>` for them to actually be
available for use by `tox`.

# Package and Container Image Building

An [RPM spec file](scc-hypervisor-collector.spec) is provided which is ready
to be used by the openSUSE Build Service (OBS) to build SLE 15 SP2/3/4 based
RPMs. The packaging process leverages the service and timer scripts provided
under the [systemd directory](systemd).

Additionally a [Dockerfile](container/Dockerfile) (suitable for building a
container image in OBS) and an accompanying [entrypoint script](container/entrypoint.bash)
are provided in the [container directory](container).

## Version Management

The `bin/bumpversion` command should be used to update the version of the
`scc-hypervisor-collector` tool, following semantic versioning practices
of `%MAJOR%.%MINOR%.%PATCH%`.

If the version bump is due to merging bug fixes and other minor changes,
then `patch` should be specified as the argument when calling `bumpversion`
which will cause the last element of the version to be incremented by one.

If the version bump is due to landing a new feature which enhances the
`scc-hypervisor-collector` in a backwards compatible way, then `minor` should
be specified as the the argument to `bumpversion` which will increments the
middle element of the version and resets the last element to `0`.

If the version bump is due to landing new features or other functionality
changes that are not backwards compatible, then `major` should be passed as
the argument when calling `bumpversion` which will increment the first element
of the version and resets middle and last elements to `0`.

After running the `bumpversion` command the resulting change should be proposed
as a new PR, to be reviewed, approved, and eventually merged.

## Version Tagging

Whenever the version is updated, once the PR that contains the version change
has merged, a matching new version tag in the format of `v%VERSION%` should be
created and pushed to the repository using commands similar to the following,
where `%old_version%` and `%new_version%` are, respectively, the previous and
updated versions:

```
% git tag -m "Bump version: %old_version% → %new_version%" "v%new_version%" origin/main
% git push --tags origin
```

## Package and Container Versioning

The current OBS based package build workflow will automatically set the RPM
package verison to `%VERSION%~git%TAG_OFFSET%.%GIT_SHA%`, so even merged PR
will result in an updated version. And the same version info will be used to
generate the version tags for the container image that will be rebuilt in OBS
whenever the main package gets updated.

See [OBS Maintenance Workflow](doc/OBS_Maintance_Workflow.md) for more details
on how to ensure that the RPM package is rebuilt to pick up the latest changes
to the `scc-hypervisor-collector` sources, setup scripts, spec file and systemd
unit files, as well as how to ensure the container build picks up the latest
changes to the [Dockerfile](container/Dockerfile) and [entrypoint.bash](container/entrypoint.bash)
scripts.

# Running the scc-hypervisor-collector

See the [man pages](doc/man) for details about running the command locally.

See [Security Recommendations](doc/Security.md) for further details about
ensuring the configuration settings and runtime environment for the command
are correctly setup.

See [Container Deployment](doc/Container_Deployment.md) for details on how to
run the command using a container image built using the provided [Dockerfile](container/Dockerfile)
and the [Open Build Service](https://build.opensuse.org).

# The scc-hypervisor-collector design
The tool is broken down into a number of component APIs which are implemented as
subpackages within the main `scc-hypervisor-collector` package.

## `Inputs` - Configuration directory and files
The config directory and files provided as arguments for the tool has 
sensitive information that needs to be protected. The tool requires 
these to be owned by the user running the tool. The permissions on these 
config files need to be read/write (0600) and the config directory should 
be user access only (0700) for the user that will run the tool. 
The tool cannot be run with root privileges. 

## `ConfigManager` - Configuration Management
The `ConfigManager` class is implemented in
[api/config_manger.py](src/scc-hypervisor-collector/api/config_manager.py)
and leverages the various configuration management classes found in
[api/configuration.py](src/scc-hypervisor-collector/api/configuration.py)
to load and validate the `scc-hypervisor-collector` configuration data.

## `HypervisorCollector` - Collector for Hypervisor details
The `HypervisorCollector` class is implemented in
[api/hypervisor_collector.py](src/scc-hypervisor-collector/api/hypervisor_collector.py)
and leverages the
[Virtual Host Gatherer](https://github.com/uyuni-project/virtual-host-gatherer/)
as a Python3 library to collect relevant details from the conigfured hypervisor
solution.

## `CollectionScheduler` - Schedules Hypervisor collection and SCC uploads
The `CollectionScheduler` class is implemented in
[api/scheduler.py](src/scc-hypervisor-collector/api/scheduler.py) and is
responsible for scheduling the retrieval of details from the configured
hypervisor solutions.

## `SCCUploader` - Uploads collected Hypervisor details to SCC
The `SCCUploader` class is implemented in
[api/uploader.py](src/scc-hypervisor-collector/api/uploader.py) and is used
to upload collected hypervisor details to the SUSE Customer Center via the
[organizations/virtualization_hosts](https://scc.suse.com/connect/v4/documentation#/organizations/put_organizations_virtualization_hosts) API.

## `cli` - CLI wrapper that drives the other APIs
The `scc_hypervisor_collector.cli:main` routine is implemented in
[cli/__init__.py](src/scc-hypervisor-collector/cli/__init__.py)
and provides the command line interface for `scc-hypervisor-collector`.

# Configuration Examples
See the [examples directory](examples) for examples of configuration
settings:

* [all_in_one](examples/all_in_one) shows an example of specifying all
  of the settings in a single configuration file.
* [creds_and_backends](examples/creds_and_backends) shows an example of
  specifying the credentials settings in one configuration file and the
  backends settings in another configuration file.
* [multiple_files](examples/multiple_files) shows an example of specifying
  the credentials settings in one configuration file and the various
  backends settings in backend type specific configuration files.
