# python-canfar-clients
This repository contains Python client libraries and command-line utilities for interacting with [CANFAR](http://www.canfar.phys.uvic.ca/) and [CADC](http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/) web services, under `canfar-clients/` and `cadc-clients/`, respectively. `canfar-cloud-clients/` contains a package that extends `canfar-clients` to interact with CANFAR services that depend on external OpenStack cloud providers. See the individual `README.md` in each package directory for further details.

```
python-canfar-clients
|
|--canfar-clients        # Root of "canfar" package
|  |--canfar             # canfar
|  |  |--common          # canfar.common
|  |  +--groups          # canfar.groups
|  |--scripts            # command-line scripts
|  +--test               # integration tests
|
|--cadc-clients          # Root of "cadc" package, depends on "canfar"
|  |--cadc               # cadc
|  |  +--data            # cadc.data
|  |--scripts            # command-line scripts
|  +--test               # integration tests
|
+--canfar-cloud-clients  # Root of "canfarcloud" package, depends on "canfar"
   |--canfar             # canfar -- extends namespace package "canfar"
   |  +--proc            # canfar.proc
   |--scripts            # command-line scripts
   +--test               # integration tests
```


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
$ python setup.py install
$ cd ..
```

Finally, install any remaining external dependencies for `cadc-clients` and
develop/install it in the **venv** as well:
```
$ pip install -r cadc-clients/requirements.txt
$ cd cadc-clients
$ python setup.py install
$ cd ..
```

Similarly, `canfar-cloud-clients` extends (and therefore depends on) `canfar-clients`, so it may also be developed/installed once `canfar-clients` is installed in the **venv**:
```
$ pip install -r canfar-cloud-clients/requirements.txt
$ cd canfar-cloud-clients
$ python setup.py instal
$ cd ..
```
