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

from f5.bigip import BigIP as BigIPSDK
import heat_client_utils as hc_utils
import plugin_test_utils as plugin_utils
import pytest
from pytest import symbols as symbols_data


def create_stack(template, parameters={}):
    hc = hc_utils.HeatClientMgr(
        symbols_data.username,
        symbols_data.tenant_password,
        symbols_data.tenant_name,
        symbols_data.auth_url,
        symbols_data.teststackname,
        symbols_data.heat_endpoint
    )
    parameters.update(
        {'bigip_ip': symbols_data.bigip_ip,
         'bigip_un': symbols_data.bigip_username,
         'bigip_pw': symbols_data.bigip_password}
    )

    stack = hc.create_stack(template=template, parameters=parameters)
    return hc, stack


@pytest.fixture
def HeatStack(request):
    '''Heat stack fixture for creating/deleting a heat stack.'''
    def manage_stack(template_file, parameters={}):
        template = plugin_utils.get_template_file(template_file)
        hc, stack = create_stack(
            template, parameters
        )

        def teardown():
            hc.delete_stack()
        request.addfinalizer(teardown)

        return hc, stack
    return manage_stack


@pytest.fixture
def HeatStackNoTeardown(request):
    '''Heat stack fixture for creating/deleting a heat stack.'''
    def manage_stack(template_file):
        template = plugin_utils.get_template_file(template_file)
        hc, stack = create_stack(
            template
        )

        return hc, stack
    return manage_stack


@pytest.fixture
def HeatStackNoParams(request, symbols):
    '''Heat stack fixture which gives no params to create_stack.'''
    def manage_stack(template_file):

        template = plugin_utils.get_template_file(template_file)
        hc = hc_utils.HeatClientMgr(
            symbols_data.username,
            symbols_data.tenant_password,
            symbols_data.tenant_name,
            symbols_data.auth_url,
            symbols_data.teststackname,
            symbols_data.heat_endpoint
        )
        stack = hc.create_stack(template=template)

        def teardown():
            hc.delete_stack()
        request.addfinalizer(teardown)

        return hc, stack
    return manage_stack


@pytest.fixture
def BigIP():
    '''BigIP fixture.'''
    return BigIPSDK(
        symbols_data.bigip_ip,
        symbols_data.bigip_username,
        symbols_data.bigip_password
    )
