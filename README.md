# python-canfar-clients
This repository contains Python client libraries and command-line utilities for interacting with [CANFAR](http://canfar.phys.uvic.ca/) and [CADC](http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/) web services, under `canfar-clients/` and `cadc-clients/`, respectively.

## Shared virtual environment
If you are working on `cadc-clients` you will also want to have `canfar-clients` installed, as it is a dependency. In this event a shared virtual environment (**venv**) will be useful.

First install **virtualenv**:
```
$ pip install virtualenv
```

Next create, and activate, a local **venv** (this example uses **bash**) in the root directory of this repository:
```
$ virtualenv venv
$ source venv/bin/activate

```

Then, install the missing external dependencies for `canfar-clients`, and build
build and install it to the **venv**:
```
$ pip install -r canfar-clients/requirements.txt
$ cd canfar-clients
$ python setup.py instal
$ cd ..
```

Finally, install any remaining external dependencies for `cadc-clients` and
develop/install it in the **venv** as well:
```
$ pip install -r cadc-clients/requirements.txt
$ cd cadc-clients
$ python setup.py install
```

