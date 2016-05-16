# canfar
This Python package provides client libraries and command-line utilities for interacting with [CANFAR](http://www.canfar.phys.uvic.ca/) web services.

## Installation
The `requirements.txt` file can be used to install all necessary dependencies globally:
```
$ sudo pip install -r requirements.txt
```

Or to upgrade (this may be required if you see errors like `ImportError: No module named packages.urllib3.poolmanager`).
```
$ sudo pip install --upgrade -r requirements.txt
```

If **pip** fails, you may need to install other missing system dependencies before trying again.

For example, with Ubuntu 14.04:
```
$ sudo apt-get install python-pip libssl-dev libffi-dev libxml2-dev libxslt1-dev python-dev
```

With CentOS 6.5 / 7:
```
$ sudo yum install gcc python-pip openssl-devel libffi-devel libxslt-devel python-devel
```

After that, to install this project globally:
```
$ sudo python setup.py install
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
$ canfar-is-member --help
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
$ cd canfar/groups/test
$ python test_client.py
```
or with additional options to calculate coverage:
```
$ python -m trace --count -s -m --ignore-dir=${VIRTUAL_ENV}:/usr test_client.py
```
