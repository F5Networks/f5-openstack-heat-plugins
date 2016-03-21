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
    default: admin
  bigip_pw:
    type: string
    default: admin
  bigip_ip:
    type: string
    default: 10.190.6.9

resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      username: { get_param: bigip_un }
      password: { get_param: bigip_pw }
      ip: { get_param: bigip_ip }
'''

wrong_ip_template = '''
heat_template_version: 2015-04-30
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      username: admin
      password: admin
      ip: 127.0.0.1
'''

bad_pass_template = '''
heat_template_version: 2015-04-30
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      username: admin
      password: badpassword
      ip: 10.190.4.147
'''


bad_prop_template = '''
heat_template_version: 2015-04-30
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      username: admin
      password: admin
      ip: 10.190.4.147
      bad_extra_prop: cooldeal
'''


def test_create_complete(BigIPDevice):
    hc, stack = BigIPDevice(test_template)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True


def test_create_failed_bad_ip(BigIPDevice):
    hc, stack = BigIPDevice(wrong_ip_template)
    assert utils.wait_until_status(hc, stack.id, 'create_failed') is True
    failed_stack = utils.get_stack(hc, stack.id)
    assert 'Failed to establish a new connection' in \
        failed_stack.stack_status_reason


def test_create_failed_bad_password(BigIPDevice):
    hc, stack = BigIPDevice(bad_pass_template)
    assert utils.wait_until_status(hc, stack.id, 'create_failed') is True
    failed_stack = utils.get_stack(hc, stack.id)
    assert 'Failed to establish a new connection' in \
        failed_stack.stack_status_reason


def test_create_bad_property(BigIPDevice):
    hc, stack = BigIPDevice(bad_prop_template)
    assert utils.wait_util_status(hc, stack.id, 'create_failed') is True
    failed_stack = utils.get_stack(hc, stack.id)
    print(failed_stack)
    assert True is False
