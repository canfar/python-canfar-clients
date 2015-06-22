# python-cadc-clients
This repository contains Python client libraries and command-line utilities for interacting with [CADC](http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/) and [CANFAR](http://canfar.phys.uvic.ca/) web services.

## Installation
The `requirements.txt` file will install all necessary dependencies:
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

This behaviour may be overriden by specifying an alternative proxy certificate location (`--certfile=[location]`), or forcing an anonymous connection (`--anonymous`).

For further help on the usage of the following clients, provide the `--help` option.

### CADC storage service
Copy files to and from the CADC storage service. An archive must always be specified, and a stream may also be supplied optionally, as well as different file names on-disk and in the archive:

```
$ cadc-copy put ARCHIVE /local/file
$ cadc-copy get ARCHIVE /some/file
$ cadc-copy get ARCHIVE /some/local/filename --stream=RAW --filename=nameInArchive
```

### CANFAR groups service
To check whether the identity of a user stored in their certificate is a member of a CANFAR group (presently name/password authentication is not supported for this service):
```
$ canfar-is-member groupname
```

Groups can also be created:
```
$ canfar-create-group groupname
```
and queried:
```
$ canfar-get-group groupname
```

## Development
Common base classes and CADC-specific modules reside in the `cadc/` package. CANFAR-specific modules in `canfar/`.

A virtual environment (venv) is used to set up external dependencies. Presently an **ant** build file is used for integration with the CADC build system, and the following target will create the venv:
```
$ ant test
```
This will create a directory with a name like `/tmp/python-cadc-clients124042940`. To activate the virtual environment (primarily placing local packages and Python libraries at the head of `PATH` and `PYTHONPATH`):
```
$ source /tmp/104019941/bin/activate
```
All dependencies that are not available globally (defined in requirements.txt) should now be available.

Doing things like `python setup.py install` will install the package to this temporary directory.

### Unit Tests
The top-level `rununittests` executes unit tests in `[cadc/canfar]/<package>/test` and displays coverage statistics. For detailed line-by-line coverage see the `*.cover` files that reside in the same directories as the source files `*.py` that were executed by the tests.

### Integration Tests
The integration tests are, at present, designed to run only at CADC. For this to work, you will probably want to do the following:
1. Set the environment variable `$CADC_ROOT` to the path where CADC software are installed.
2. Install the clients (to the venv) using `$ python setup.py install`
3. `$ test/inttest`
