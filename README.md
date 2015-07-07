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
|  |  |--canfar-create-group
|  |  |--canfar-get-group
|  |  +--canfar-is-member
|  +--test               # integration tests
|
|--cadc-clients          # Root of "cadc" package, depends on "canfar"
|  |--cadc               # cadc
|  |  +--data            # cadc.data
|  |--scripts            # command-line scripts
|  |  |--cadc-copy
|  |  +--cadc-fileinfo
|  +--test               # integration tests
|
+--canfar-cloud-clients  # Root of "canfarcloud" package, depends on "canfar"
   |--canfar             # canfar -- extends namespace package "canfar"
   |  +--proc            # canfar.proc
   |--scripts            # command-line scripts
   |  +--canfar-job-submit
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
and install it to the **venv**:
```
$ pip install -r canfar-clients/requirements.txt
$ cd canfar-clients
$ python setup.py install
$ cd ..
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

## Releases to PyPI
Stable releases of these packages are provided through [PyPI](https://pypi.python.org/pypi). It should therefore be possible to install any package using:
```
$ pip install canfar
$ pip install cadc
$ pip install canfarcloud
```
and **pip** will resolve and install dependencies. Again, note that if **pip** fails you probably need to install additional system dependencies as described above.

If you see errors when using applications, particularly things like `ImportError: No module named packages.urllib3.poolmanager` use the **pip** option `--upgrade` to ensure that the dependencies are upgraded to their latest versions.

In order to create a new release on **PyPI**, enter the package directory where `setup.py` resides. Increment the version number (`canfar/__version__.py` is shared by `canfar-clients/` and `canfar-cloud-clients/`, and `cadc/__version__.py` for `cadc-clients/`). Then, issue the following commands:
```
$ python setup.py register -r pypi
$ python setup.py sdist upload -r pypi
```

These instructions assume you have an account on `PyPI` and an associated `~/.pypirc` with your name and password, and permission to update the package. [This page](http://peterdowns.com/posts/first-time-with-pypi.html) is a useful reference.

Once you have created a release, create and push a new tag in the git repository.
```
$ git tag canfar-0.2.2
$ git push --tags
```
