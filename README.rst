f5-openstack-heat-plugins
=========================
.. image:: https://travis-ci.org/F5Networks/f5-openstack-heat-plugins.svg?branch=kilo
    :target: https://travis-ci.org/F5Networks/f5-openstack-heat-plugins

.. image:: https://readthedocs.org/projects/f5-openstack-heat-plugins/badge/?version=kilo
    :target: http://f5-openstack-heat-plugins.readthedocs.org/en/latest/?badge=kilo

Introduction
------------
This repository houses all of F5®'s OpenStack Heat resource plugins. F5®'s
Heat plugins can be used to orchestrate BIG-IP®  services in your OpenStack environment.

Releases and Versions
---------------------
This branch supports the OpenStack Kilo release.

For more information about F5® Networks's OpenStack versioning and a support
matrix please see `F5® Networks OpenStack Support Matrix <http://f5-openstack-docs.readthedocs.org/en/latest/releases_and_versioning.html>`__.

Installation
------------
The Heat plugins must be installed on the machine where the Heat engine
service is running in your stack. 'sudo' access on this machine may be needed.
The Python tool 'pip' is being used to install. Once the plugins are installed,
you must either tell the Heat engine service where to find the installed
plugins or link (or copy) the plugins to a location where the Heat engine is
already expecting to find new plugins. The Heat configuration file in
'/etc/heat/heat.conf' has an option called 'plugin_dirs', which defines the
default locations the Heat engine seraches for new plugins. In the steps below
we will link the plugins to a location where Heat is expecting new plugins to
be. Please remember that your installation may differ (sometimes greatly) from
 what we show below.

*Note: If you are installing a pre-release version of the package with pip
you will need to use the --pre option.*

Ubuntu
~~~~~~
.. code:: shell

   $ apt-get install python-pip
   $ pip install f5-openstack-heat-plugins
   # Link (or copy) plugins to the Heat plugin directory
   # This directory may not exist
   $ mkdir -p /usr/lib/heat
   $ ln -s /usr/lib/python2.7/dist-packages/f5_heat /usr/lib/heat/f5_heat
   $ service heat-engine restart

RedHat/CentOS
~~~~~~~~~~~~~
.. code:: shell

   $ yum install python-pip
   $ pip install f5-openstack-heat-plugins
   # Link (or copy) plugins to the Heat plugin directory
   # This directory may not exist
   $ mkdir -p /usr/lib/heat
   $ ln -s /usr/lib/python2.7/site-packages/f5_heat /usr/lib/heat/f5_heat
   $ systemctl restart openstack-heat-engine.service

Usage
-----
Once the plugins are installed the F5 objects can be used when creating Heat
templates.  An example use of one of the objects is below.

.. code:: yaml

    resources:
      # The first two resources defined here are requirements for deploying
      # any object on the BigIP VE. The F5::BigIP::Device allows access and
      # authentication to the BigIP on which an object will be configured.
      # The F5::Sys::Partition resource places a particular object in the
      # partition given. These two requirements will be linked with the obects
      # we intend to configure (iAppTemplate, iAppService) by calling the
      # 'get_resource' intrinsic function.
      bigip:
        type: F5::BigIP::Device
        properties:
          ip: 10.0.0.1 # All properties can be passed in as parameters
          username: admin
          password: admin # The password can be passed in as a hidden field
      partition:
        type: F5::Sys::Partition
        properties:
          name: Common # Put these objects in the existing Common partition
          bigip_server: { get_resource: bigip } # Create dependency on bigip
      iapp_template:
        type: F5::Sys::iAppTemplate
        properties:
          name: test_template
          bigip_server: { get_resource: bigip } # Depends on bigip resource
          partition: { get_resource: partition} # Depends on partition as well
          full_template:
            get_file: iapps/full_template.tmpl
      iapp_service:
        type: F5::Sys::iAppService
        properties:
          name: test_service
          bigip_server: { get_resource: bigip }
          partition: { get_resource: partition }
          template_name: test_template # Matches name in template resource


Documentation
-------------
Project documentation can be found on `Read The Docs <https://f5-openstack-heat-plugins.readthedocs.org>`_.

Filing Issues
-------------
If you find an issue we would love to hear about it. Please let us know by
filing an issue in this repository and tell us as much as you can about what
you found and how you found it.

Contributing
------------
See `Contributing <CONTRIBUTING.md>`_.

Build
-----
To make a PyPI package...

.. code:: bash

    $ python setup.py sdist


Test
----
Before you open a pull request, your code must have passing `pytest <http://pytest.org>`__ unit tests. In addition, you should include a set of functional tests written to use a real BIG-IP®  device
for testing. Information on how to run our set of tests is included below.

Unit Tests
~~~~~~~~~~
We use pytest for our unit tests.

#. If you haven't already, install requirements.unit.test.txt in your virtual
   environment.

.. code:: shell

   $ pip install hacking pytest pytest-cov
   $ pip install -r requirements.txt

#. Run the tests and produce a coverage report. The ``--cov-report=html`` will create a ``htmlcov/`` directory that you can view in your browser to see the missing lines of code.

.. code:: shell
       $ pip install -r requirements.unit.test.txt

#. | Run the tests and produce a coverage report. The
     ``--cov-report=html`` will
   | create a ``htmlcov/`` directory that you can view in your browser
     to see the
   | missing lines of code.
       py.test --cov f5_heat/resources/test --cov-report=html
       open htmlcov/index.html

Functional Tests
~~~~~~~~~~~~~~~~
Pytest is also used for functional tests

#. If you haven't already, install requirements.func.test.txt in your virtual
   environment.

   .. code:: shell

       $ pip install -r requirements.func.test.txt

#. | Currently, you must modify ``test/functional/test_variables.py`` file to
     provide the proper credentials to Openstack. See that file for more info
     on what is needed. Also remember not to include this file in your pull
     request, since it may contiain sensitive information.

#. | Run the functional tests and pass in arguments to connect to the F5® Device.

   .. code:: shell

       py.test test/functional/ --bigip=<bigip_ip> --bigip-username=<web_login_username> --bigip-passwword=<web_login_password>

Style Checks
~~~~~~~~~~~~
We use the hacking module for our style checks (installed as part of step 1 in the Unit Test section).

.. code:: shell

    $ flake8 ./


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
have completed and submitted the `F5® Contributor License
Agreement <http://f5-openstack-docs.readthedocs.org/en/latest/cla_landing.html>`__
to Openstack_CLA@f5.com prior to their code submission being included in this
project.
