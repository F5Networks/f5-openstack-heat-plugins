# Copyright 2015-2016 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import plugin_test_utils as utils

test_template = '''
heat_template_version: 2015-04-30
description: testing stack creation in python
parameters:
  bigip_un:
    type: string
  bigip_pw:
    type: string
  bigip_ip:
    type: string

resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      username: { get_param: bigip_un }
      password: { get_param: bigip_pw }
      ip: { get_param: bigip_ip }
  partition:
    type: F5::Sys::Partition
    properties:
      name: Common
      bigip_server: { get_resource: bigip_rsrc }
'''

new_partition_template = '''
heat_template_version: 2015-04-30
parameters:
  bigip_un:
    type: string
  bigip_pw:
    type: string
  bigip_ip:
    type: string
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      username: { get_param: bigip_un }
      password: { get_param: bigip_pw }
      ip: { get_param: bigip_ip }
  partition:
    type: F5::Sys::Partition
    properties:
      name: test_partition
      bigip_server: { get_resource: bigip_rsrc }
'''

bad_subpath_template = '''
heat_template_version: 2015-04-30
parameters:
  bigip_un:
    type: string
  bigip_pw:
    type: string
  bigip_ip:
    type: string
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      username: { get_param: bigip_un }
      password: { get_param: bigip_pw }
      ip: { get_param: bigip_ip }
  partition:
    type: F5::Sys::Partition
    properties:
      name: test_partition
      bigip_server: { get_resource: bigip_rsrc }
      subpath: /BadSubPath/
'''


def test_create_complete(HeatStack):
    hc, stack = HeatStack(test_template)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True


def test_create_complete_new_partition(HeatStackNoTeardown, BigIP):
    hc, stack = HeatStackNoTeardown(new_partition_template)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True
    assert BigIP.sys.folders.folder.exists(name='test_partition') is True
    utils.delete_stack(hc, utils.TESTSTACKNAME)
    assert BigIP.sys.folders.folder.exists(name='test_partition') is False


def test_create_failed_bad_subpath(HeatStack, BigIP):
    msg = '(/BadSubPath) folder does not exist'
    hc, stack = utils.ensure_failed_stack(HeatStack, bad_subpath_template, msg)
    assert BigIP.sys.folders.folder.exists(name='test_partition') is False
