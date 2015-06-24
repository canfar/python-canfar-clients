# python-clients
This repository contains Python client libraries and command-line utilities for interacting with [CADC](http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/) and closely-related [CANFAR](http://canfar.phys.uvic.ca/) web services, under `cadc-clients/` and `canfar-clients/`, respectively.

## Shared virtual environment
Often you will want to develop both `canfar-clients` and `cadc-clients` at the same time since the former depends on the latter. In this event a shared virtual environment (**venv**) will be useful.

First install **virtualenv**:

Next create, and activate, a local **venv** (this example uses **bash**) in the root directory of this repository:
```
$ virtualenv venv
$ source venv/bin/activate

```

Next, install the missing external dependencies from *both* packages:
```
$ pip install -r cadc-clients/requirements.txt
$ pip install -r canfar-clients/requirements.txt

```

If you are working on `canfar-clients` you will need to have `cadc-clients` installed in the **venv** first, so:
```
$ cd cadc-clients
$ python setup.py install
$ cd ../canfar-clients
```

