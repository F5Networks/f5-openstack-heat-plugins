F5 OpenStack Heat Plugins Documentation
=======================================

Introduction
------------
This repository houses all of F5's `Openstack Heat <https://wiki.openstack.org/wiki/Heat>`__
resource plugins. F5's Heat plugins can be used to orchestrate BIG-IP services
in your OpenStack environment.

Releases and Versions
---------------------
|release| supports the OpenStack |openstack_release| release.

For more information about F5 Networks's OpenStack versioning and a support
matrix please see `F5 Networks OpenStack Releases and Support Matrix
<http://f5networks.github.io/f5-openstack-docs/releases_and_versioning/>`__

Installation
------------
The heat plugins must be installed on the machine that the Heat engine is
running on in order to use templates that refer to the F5 plugins.  After
installing the plugins the Heat engine must be restarted for them to take
effect.

*Note: If you are installing a pre-release version of the package with pip
you will need to use the --pre option.*

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
Maintenance and support of the unmodified F5 code is provided only to customers
who have an existing support contract, purchased separately subject to F5’s
support policies available at http://www.f5.com/about/guidelines-policies/ and
http://askf5.com.  F5 will not provide maintenance and support services of
modified F5 code or code that does not have an existing support contract.

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
have completed and submitted the `F5 Contributor License
Agreement <http://f5networks.github.io/f5-openstack-docs/cla_landing/index.html>`__
to Openstack_CLA@f5.com prior to their code submission being included in this
project.


