# canfar-cloud
This Python package extends the **canfar** package by providing client libraries and command-line utilities for interacting with [CANFAR](http://www.canfar.phys.uvic.ca/) services that depend on external OpenStack cloud providers. It is packaged separately due to the significantly larger external dependencies on [OpenStack](https://www.openstack.org/).

## Installation
The `requirements.txt` file can be used to install all necessary dependencies globally:
```
$ pip install -r requirements.txt
```

Or to upgrade.
```
$ pip install --upgrade -r requirements.txt
```

After that, to install this project:
```
$ python setup.py install
```

See
```
$ python setup.py install --help
```
for additional options (e.g., `--prefix`, `--install-scripts`)

## Usage
The command-line client scripts provided by this package communicate both with OpenStack and CANFAR web servers. At present, the authentication systems have not been fully integrated, and it is assumed that a CANFAR user with username `jane` will have a mirror OpenStack account with username `jane-canfar`, and the same password in both cases. Rather than using the certificate or `.netrc` style of authentication as for other CANFAR clients, these scripts follow the OpenStack convention of specifying: (i) name; (ii) password; (iii) tenant name; and (iv) OpenStack auth service URL, typically by sourcing an [OpenStack RC File](http://www.canfar.net/docs/cli/#setup-the-environment), or specifying their values directly on the command-line.

### Submit batch job to the proc service

```
$ canfar-submit-job job.sub vm_image p1-1.5gb
```

See the [CANFAR batch documentation](http://www.canfar.net/docs/batch/) for further details.


## Development
A virtual environment (**venv**) is recommended to set up external dependencies without installing them system-wide. Following [these instructions](http://docs.python-guide.org/en/latest/dev/virtualenvs/), install **virtualenv**:
```
$ pip install virtualenv
```

Next, create, and activate a local **venv** (this example uses **bash**):
```
$ virtualenv venv
$ source venv/bin/activate

```

Finally, use **pip** to install missing external dependencies into this subdirectory:
```
$ pip install -r requirements.txt
```

It should now be possible to run the unit tests as described below.

To install the Python packages and executable scripts in the **venv**:
```
$ python setup.py install
```
You should then be able to run them, e.g.:
```
$ canfar-submit-job --help
```

Each time you resume work on the project and want to use the **venv** (e.g., from a new shell), simply re-activate it:
```
$ source venv/bin/activate
```

**Notes:**
1. There is an **ant** `build.xml` file used at the CADC for integration with the continuous build system. The `test` target can be used to create a **venv** (although it is placed under `/tmp/`). Most developers need not concern themselves with `build.xml`.
2. `requirements.txt` (used above with **pip**) has the full list of requirements for development (including tests), whereas the `requires` field in `setup.py` is used by **setuputils** to determine dependencies only for the *installed* packages/scripts (i.e., some things like **mock** are not needed by normal users).

### Unit Tests
The top-level `rununittests` executes all of the unit tests in `canfar/<package>/test` and displays coverage statistics. For detailed line-by-line coverage see the `*.cover` files that reside in the same directories as the source files `*.py` that were executed by the tests.

Alternatively, during development, individual tests may be executed from the appropriate directory, e.g.:
```
$ cd canfar/proc/test
$ python test_client.py
```
or with additional options to calculate coverage:
```
$ python -m trace --count -s -m --ignore-dir=${VIRTUAL_ENV}:/usr test_client.py
```

### Integration Tests

Presently there is only a minimal test stub in `test/inttest`.
