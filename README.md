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

## Stable Releases
Stable releases of these packages are provided through [PyPI](https://pypi.python.org/pypi). It should therefore be possible to install any of the packages using:
```
$ pip install canfar
$ pip install cadc
$ pip install canfarcloud
```
and **pip** will resolve and install dependencies. If **pip** fails you probably need to install additional system dependencies.

For example, with Ubuntu 14.04:
```
$ sudo apt-get install python-pip libssl-dev libffi-dev libxml2-dev libxslt1-dev python-dev
```

With CentOS 6.5 / 7:
```
$ sudo yum install gcc python-pip openssl-devel libffi-devel libxslt-devel python-devel
```

If you see errors when using applications, particularly things like `ImportError: No module named packages.urllib3.poolmanager` try using **pip** to install a newer version of the package that is causing problems:
```
$ pip install --upgrade urllib3
```

### canfarcloud on CentOS 6.5 / Python 2.6
While the **canfar** and **cadc** packages should work with CentOS 6.5 using Python 2.6 without any extra work, it is more difficult to get **canfarcloud** to install due to the OpenStack client dependencies which **pip** is unable to build. To circumvent this problem, use **yum** to install older packaged versions of the clients from the [RDO respository](https://www.rdoproject.org):
```
$ sudo yum install http://repos.fedorapeople.org/repos/openstack/openstack-icehouse/rdo-release-icehouse-3.noarch.rpm
$ sudo yum install python-glanceclient python-keystoneclient python-novaclient
```

Then install **canfarcloud** using **pip** (this will automatically install the **canfar** dependency as well):
```
$ sudo pip install canfarcloud
```

Again, as noted above, you may see errors regarding **urllib3** which can be fixed by upgrading the package using **pip**.

## Development with shared virtual environment
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

## Create new release on **PyPI**
When a new version of a package is ready, the work (typically performed in a branch through a GitHub pull request) should be merged into master.

Then, to create a new release on **PyPI**, enter the package directory where `setup.py` resides. Increment the version number used by the package in question (one of `canfar-clients/canfar/__version__.py`, `canfar-cloud-clients/canfar/__canfarcloud_version__.py`, or `cadc-clients/cadc/__version__.py`). Then, issue the following command:
```
$ python setup.py sdist upload -r pypi
```

These instructions assume you have an account on `PyPI` and an associated `~/.pypirc` with your name and password, and permission to update the package. [This page](http://peterdowns.com/posts/first-time-with-pypi.html) is a useful reference.

Finally, once you have uploaded the release, create and push a new tag in the git repository, e.g.,
```
$ git tag canfar-0.2.2
$ git push --tags
```
