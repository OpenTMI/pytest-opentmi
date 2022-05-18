## pytest reporting plugin for opentmi

[![Unit tests](https://github.com/OpenTMI/pytest-opentmi/actions/workflows/build-test.yml/badge.svg)](https://github.com/OpenTMI/pytest-opentmi/actions/workflows/build-test.yml)
[![PyPI version](https://badge.fury.io/py/pytest-opentmi.svg)](https://badge.fury.io/py/pytest-opentmi)
<!-- [![Coverage Status](https://coveralls.io/repos/github/OpenTMI/pytest-opentmi/badge.svg)](https://coveralls.io/github/OpenTMI/pytest-opentmi) -->


pytest plugin to upload results to opentmi server.
Plugin collect various metadata against opentmi Result -schema.
User can extend details using pytest metadata plugin.

## Usage

Install using pip:

`pip install pytest-opentmi`

plugin is enabled by using `--opentmi` CLI argument.

Running with pytest:

`pytest --opentmi <host> --opentmi_token <token> [--opentmi_store_logs]`


### Configuration

* env variable `OPENTMI_MAX_EXEC_NOTE_LENGTH` can be used to cut long failure notes. Default 1000 characters.

### metadata

module utilize some special pytest metadata keys.
Usage:

`pytest --metadata <KEY> <VALUE> ...`

**Keys:**

* Device Under Test:
  * `DUT_TYPE`  (hw, simulator)
  * `DUT_SERIAL_NUMBER`
  * `DUT_VERSION`
  * `DUT_VENDOR`
  * `DUT_MODEL`
  * `DUT_PROVIDER`

* Software Under Test:
  * `SUT_COMPONENT` (array)
  * `SUT_FEATURE` (array)
  * `SUT_COMMIT_ID`
  * `SUT_BRANCH`
