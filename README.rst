f5-openstack-heat-plugins
=========================
|Build Status|

Introduction
------------
This repository houses all of F5's Openstack Heat resource plugins. F5's
Heat plugins can be used to orchestrate BIG-IP services in your
OpenStack environment.

Installation
------------
The heat plugins need to be installed on the machine that the Heat engine is
running on in order to use templates that refer the the F5 plugins.  After
installing the plugins the Heat engine must be restarted for them to take
effect.

Ubuntu
~~~~~~
.. code:: shell

   $ pip install f5-openstack-heat-plugins
   $ service heat-engine restart

RedHat/CentOS
~~~~~~~~~~~~~
.. code:: shell

   $ pip install f5-openstack-heat-plugins
   $ systemctl restart openstack-heat-engine.service

Usage
-----
Once the plugins are installed the F5 objects can be used when creating Heat
templates.  An example use of one of the objects is below.

.. code:: yaml

    TODO: Have Paul add his simple example here

Documentation
-------------
Project documentation can be found on
`Read The Docs <https://f5-openstack-heat-plugins.readthedocs.org>`__.

Filing Issues
-------------
If you find an issue we would love to hear about it. Please let us know by
filing an issue in this repository and tell us as much as you can about what
you found and how you found it.

Contributing
------------
See `Contributing <CONTRIBUTING.md>`__

Build
-----
To make a PyPI package...

.. code:: bash

    python setup.py sdist

Test
----
Before you open a pull request, your code must have passing
`pytest <http://pytest.org>`__ unit tests. In addition, you should
include a set of functional tests written to use a real BIG-IP device
for testing. Information on how to run our set of tests is included
below.

Unit Tests
~~~~~~~~~~
We use pytest for our unit tests

#. If you haven't already, install the required test packages and the
   requirements.txt in your virtual environment.

   .. code:: shell

       $ pip install hacking pytest pytest-cov
       $ pip install -r requirements.txt

#. | Run the tests and produce a coverage repor. The
     ``--cov-report=html`` will
   | create a ``htmlcov/`` directory that you can view in your browser
     to see the
   | missing lines of code.

   .. code:: shell

       py.test --cov ./icontrol --cov-report=html
       open htmlcov/index.html

Style Checks
~~~~~~~~~~~~
We use the hacking module for our style checks (installed as part of
step 1 in the Unit Test section).

.. code:: shell

    flake8 ./

Contact
-------
f5_openstack_heat@f5.com

Copyright
---------
Copyright 2015-2016 F5 Networks Inc.

Support
-------
See `Support <SUPPORT.md>`__

License
-------
Apache V2.0
~~~~~~~~~~~
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.

Contributor License Agreement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Individuals or business entities who contribute to this project must
have completed and submitted the `F5 Contributor License
Agreement <http://f5networks.github.io/f5-openstack-docs/cla_landing/index.html>`__
to Openstack_CLA@f5.com prior to their code submission being included in this
project.

.. |Build Status| image:: https://travis-ci.com/F5Networks/f5-openstack-heat-plugins.svg?token=9DzDpZ48B74dRXvdFxM2&branch=master
   :target: https://travis-ci.com/F5Networks/f5-openstack-heat-plugins
