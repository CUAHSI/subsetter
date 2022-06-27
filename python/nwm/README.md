# CUAHSI Python Subsetter :: NWM

This subpackage provides methods for programmatically spatially subsetting National Water Model
(NWM) static domain files. To report bugs or request new features, submit an issue through the
[CUAHSI Python Subsetter Issue Tracker](https://github.com/CUAHSI/subsetter/issues) on GitHub.

## Installation

In accordance with the python community, we support and advise the usage of virtual
environments in any workflow using python. In the following installation guide, we
use python's built-in `venv` module to create a virtual environment in which the
tool will be installed. Note this is just personal preference, any python virtual
environment manager should work just fine (`conda`, `pipenv`, etc. ).

```bash
# Create and activate python environment, requires python >= 3.8
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip wheel

# Install nwm subpackage
# TODO
# python3 -m pip install subsetter.nwm
```

## Usage

The following example showcases how to spatially subset NWM static domain files using bounding box
coordinates in the WGS84 system.

### Code

TODO

### System Requirements

TODO

## Development

This package uses a setup configuration file (`setup.cfg`) and assumes use of the `setuptools` backend to build the package. To install the package for development use:

```bash
python3 -m venv env
source env/bin/activate
python3 -m pip install -U pip setuptools
python3 -m pip install -e ".[develop]"
```
