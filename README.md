![Unit Testing Status](https://github.com/CUAHSI/subsetter/actions/workflows/run_unit_tests.yml/badge.svg)

# CUAHSI Python Subsetter

## Documentation

Will be added in future.

## Motivation

Installing, configuring, running, and evaluating hydrologic models is not always straightforward and
frequently requires a wealth of tooling, datasets, esoteric knowledge, and patience. CUAHSI's Python
Subsetter was developed to make acquisition of hydrologic model configuration data simple and
familiar.

## What's here?

We don't all use the same model, so to reflect that reality, CUAHSI's Python Subsetter uses a
grab-what-you-need toolbox packaging style. This means, you only install the tools that you need for
your modeling work. As a result, CUAHSI Python Subsetter subpackages have fewer dependencies and new
tools can be added to the toolbox without affecting your modeling workflow!

It should be noted, we commonly refer to individual tools in the CUAHSI Python Subsetter using their
subpackage name (e.g. `nwm`). You will find this lingo in both issues and documentation.

Currently the repository has the following subpackage:

- `nwm`: Spatially subset operational National Water Model (NWM) static domain files.

## Usage

Refer to each subpackage's `README.md` or documentation for examples of how to use each tool.

## Installation

In accordance with the python community, we support and advise the usage of virtual environments in any workflow using python. In the following installation guide, we use python's built-in `venv` module to create a virtual environment in which the tools will be installed. Note this is just personal preference, any python virtual environment manager should work just fine (`conda`, `pipenv`, etc. ).

```bash
# Create and activate python environment, requires python >= 3.8
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip

# Install all tools
# TODO
# python3 -m pip install subsetter

# Alternatively you can install a single tool
#  This installs the NWM subsetter tool
# TODO
# python3 -m pip install subsetter.nwm
```

## Contribution

See our [contribution](CONTRIBUTING.md) guide if you are interested in contributing!
