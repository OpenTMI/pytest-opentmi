## pytest reporting plugin for opentmi

[![CircleCI](https://circleci.com/gh/OpenTMI/pytest-opentmi/tree/master.svg?style=svg)](https://circleci.com/gh/OpenTMI/pytest-opentmi/tree/master)
[![PyPI version](https://badge.fury.io/py/pytest-opentmi.svg)](https://badge.fury.io/py/pytest-opentmi)
<!-- [![Coverage Status](https://coveralls.io/repos/github/OpenTMI/pytest-opentmi/badge.svg)](https://coveralls.io/github/OpenTMI/pytest-opentmi) -->


pytest plugin to upload results to opentmi server.
Plugin collect various metadata against opentmi Result -schema.
User can extend details using pytest metadata plugin.

## Usage

Install using pip:

`pip install pytest-opentmi`

Running with pytest:

`pytest ...`


### metadata

module utilize some special pytest metadata keys.
Usage:

`pytest --metadata <KEY> <VALUE> ...`

**Keys:**

* Device Under Test:
  * `DUT_SERIAL_NUMBER`
  * `DUT_VERSION`
  * `DUT_VENDOR`
  * `DUT_MODEL`
  * `DUT_PROVIDER`

* Software Under Test:
  * `SUT_COMPONENT` (array)
  * `SUT_FEATURE` (array)
  * `SUT_COMMIT_ID`
