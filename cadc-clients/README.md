# CADC
This Python package provides client libraries and command-line utilities for interacting with [CADC](http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/) web services.

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
The command-line client scripts provided by this repo generally authenticate automatically using:

1. a proxy certificate in the default location `$HOME/.ssl/cadcproxy.pem` **OR**
2. username/password stored in `$HOME/.netrc` with an entry like:
        `machine www.canfar.phys.uvic.ca login [username] [password]`

If neither a proxy certificate nor an entry in `.netrc` can be found, an anonymous connection is used.

This behaviour may be overriden by specifying an alternative proxy certificate location (`--certfile=[location]`), or forcing an anonymous connection (`--anonymous`).

For further help on the usage of the following clients, use the `--help` option.

### CADC storage service
Copy files to and from the CADC storage service. An archive must always be specified, and a stream may also be supplied optionally, as well as different file names on-disk and in the archive:

```
$ cadc-copy put ARCHIVE /local/file
$ cadc-copy get ARCHIVE /some/file
$ cadc-copy get ARCHIVE /some/local/filename --stream=RAW --filename=nameInArchive
```

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
$ cadc-copy --help
```

Each time you resume work on the project and want to use the **venv** (e.g., from a new shell), simply re-activate it:
```
$ source venv/bin/activate
```

**Notes:**
1. There is an **ant** `build.xml` file used at the CADC for integration with the continuous build system. The `test` target can be used to create a **venv** (although it is placed under `/tmp/`). Most developers need not concern themselves with `build.xml`.
2. `requirements.txt` (used above with **pip**) has the full list of requirements for development (including tests), whereas the `requires` field in `setup.py` is used by **setuputils** to determine dependencies only for the *installed* packages/scripts (i.e., some things like **mock** are not needed by normal users).

### Unit Tests
The top-level `rununittests` executes all of the unit tests in `cadc/<package>/test` and displays coverage statistics. For detailed line-by-line coverage see the `*.cover` files that reside in the same directories as the source files `*.py` that were executed by the tests.

Alternatively, during development, individual tests may be executed from the appropriate directory, e.g.:
```
$ cd cadc/data/test
$ python test_client.py
```
or with additional options to calculate coverage:
```
$ python -m trace --count -s -m --ignore-dir=${VIRTUAL_ENV}:/usr test_client.py
```

### Integration Tests
The integration tests are, at present, designed to run only at CADC. Tests assume that scripts have been installed (e.g., into the **venv**). You will also need to set `CADCTESTCERTS` to the location of test certificates, and possibly set `CADC_WEBSERVICE` to the host name of a test web service.

1. `$ python setup.py install`
2. `$ test/inttest`

