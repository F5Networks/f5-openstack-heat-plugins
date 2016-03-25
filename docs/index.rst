F5® OpenStack Heat Plugins
==========================

Overview
--------
This repository houses all of F5®'s `Openstack Heat <https://wiki.openstack.org/wiki/Heat>`__
resource plugins. F5®'s Heat plugins can be used to orchestrate BIG-IP® services
in your OpenStack environment.

Releases and Versions
---------------------
|release| supports the OpenStack |openstack_release| release.

For more information about F5 Networks®' OpenStack versioning and a support
matrix, please see `F5 Networks®  OpenStack Support Matrix <http://f5-openstack-docs.readthedocs.org/en/latest/releases_and_versioning.html>`__.

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

.. note::
    If you are installing a pre-release version of the package with pip, you will need to use the ``--pre`` option.

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
Once the plugins are installed, you can use the F5® objects when creating Heat templates (example below).

.. code:: yaml

    resources:
      # The first two resources defined here are requirements for deploying
      # any object on the BIG-IP® VE. The F5::BigIP::Device allows access and
      # authentication to the BIG-IP® on which an object will be configured.
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


API Documentation
-----------------
.. toctree::
   :maxdepth: 4

   apidoc/modules.rst


Copyright
---------
Copyright 2015-2016 F5 Networks Inc.

Support
-------
See `SUPPORT.md <https://github.com/F5Networks/f5-openstack-heat-plugins/blob/master/SUPPORT.md>`_.

License
-------
Apache V2.0
~~~~~~~~~~~

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See
the License for the specific language governing permissions and limitations
under the License.

Contributor License Agreement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Individuals or business entities who contribute to this project must
have completed and submitted the `F5® Contributor License
Agreement <http://f5-openstack-docs.readthedocs.org/en/latest/cla_landing.html>`__
to Openstack_CLA@f5.com prior to their code submission being included in this
project.


