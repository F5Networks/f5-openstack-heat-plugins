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

import os

import pytest
from pytest import symbols as symbols_data

import functional.heat_client_utils as hc_utils
import functional.plugin_test_utils as utils

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def test_create_complete(HeatStack):
    hc, stack = HeatStack(os.path.join(TEST_DIR, 'success.yaml'))
    assert hc.wait_until_status(stack.id, 'create_complete') is True


def test_create_failed_bad_ip(HeatStackNoParams):
    msg = 'Failed to establish a new connection'
    utils.ensure_failed_stack(
        HeatStackNoParams, os.path.join(TEST_DIR, 'bad_ip.yaml'), msg
    )


def test_create_failed_bad_password(HeatStack):
    msg = 'F5 Authorization Required for uri'
    utils.ensure_failed_stack(
        HeatStack, os.path.join(TEST_DIR, 'bad_password.yaml'), msg
    )


def test_create_bad_property():

    bad_property_template = utils.get_template_file(
        os.path.join(TEST_DIR, 'bad_property.yaml')
    )
    with pytest.raises(Exception) as ex:
        hc = hc_utils.HeatClientMgr(
            symbols_data.username,
            symbols_data.tenant_password,
            symbols_data.tenant_name,
            symbols_data.auth_url,
            symbols_data.teststackname,
            symbols_data.heat_endpoint
        )
        hc.create_stack(template=bad_property_template)
    assert 'Unknown Property bad_extra_prop' in ex.value.message
