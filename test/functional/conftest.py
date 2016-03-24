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
import plugin_test_utils as utils

import pytest


def pytest_addoption(parser):
    parser.addoption('--bigip', action='store',
                     help='BIG-IP hostname or IP address')
    parser.addoption('--username', action='store',
                     help='BIG-IP username')
    parser.addoption('--password', action='store',
                     help='BIG-IP password')


@pytest.fixture
def opt_bigip(request):
    return request.config.getoption('--bigip')


@pytest.fixture
def opt_bigip_un(request):
    return request.config.getoption('--username')


@pytest.fixture
def opt_bigip_pw(request):
    return request.config.getoption('--password')


def create_stack(bigip_ip, bigip_un, bigip_pw, template):
    hc = utils.get_heat_client()
    stack = utils.create_stack(
        hc,
        stack_name=utils.TESTSTACKNAME,
        template=template,
        parameters={
            'bigip_ip': bigip_ip,
            'bigip_un': bigip_un,
            'bigip_pw': bigip_pw
        }
    )
    return hc, stack


@pytest.fixture
def HeatStack(opt_bigip, opt_bigip_un, opt_bigip_pw, request):
    '''Heat stack fixture for creating/deleting a heat stack.'''
    def manage_stack(stack_template):
        def teardown():
            utils.delete_stack(hc, utils.TESTSTACKNAME)
        request.addfinalizer(teardown)
        hc, stack = create_stack(
            opt_bigip, opt_bigip_un, opt_bigip_pw, stack_template
        )
        return hc, stack
    return manage_stack


@pytest.fixture
def HeatStackNoTeardown(opt_bigip, opt_bigip_un, opt_bigip_pw, request):
    '''Heat stack fixture for creating/deleting a heat stack.'''
    def manage_stack(stack_template):
        hc, stack = create_stack(
            opt_bigip, opt_bigip_un, opt_bigip_pw, stack_template
        )
        return hc, stack
    return manage_stack


@pytest.fixture
def HeatStackNoParams(request):
    '''Heat stack fixture which gives no params to create_stack.'''
    def manage_stack(stack_template):
        def teardown():
            utils.delete_stack(hc, utils.TESTSTACKNAME)

        request.addfinalizer(teardown)
        hc = utils.get_heat_client()
        stack = utils.create_stack(
            hc, stack_name=utils.TESTSTACKNAME, template=stack_template
        )
        return hc, stack
    return manage_stack


@pytest.fixture
def BigIP(opt_bigip, opt_bigip_un, opt_bigip_pw):
    '''BigIP fixture.'''
    return BigIPSDK(opt_bigip, opt_bigip_un, opt_bigip_pw)
