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

import pytest

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
      password: badpassword
      ip: { get_param: bigip_ip }
'''


bad_prop_template = '''
heat_template_version: 2015-04-30
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      username: admin
      password: admin
      ip: ip_doesnt_matter
      bad_extra_prop: cooldeal
'''


def test_create_complete(HeatStack):
    hc, stack = HeatStack(test_template)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True


def test_create_failed_bad_ip(HeatStackNoParams):
    msg = 'Failed to establish a new connection'
    utils.ensure_failed_stack(HeatStackNoParams, wrong_ip_template, msg)


def test_create_failed_bad_password(HeatStack):
    msg = 'F5 Authorization Required for uri'
    utils.ensure_failed_stack(HeatStack, bad_pass_template, msg)


def test_create_bad_property():
    with pytest.raises(Exception) as ex:
        hc = utils.get_heat_client()
        utils.create_stack(hc, stack_name='test', template=bad_prop_template)
    assert 'Unknown Property bad_extra_prop' in ex.value.message
