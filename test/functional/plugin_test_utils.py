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

from test_variables import AUTH_URL
from test_variables import HEAT_ENDPOINT
from test_variables import PASSWORD
from test_variables import TENANT_NAME
from test_variables import USERNAME

import time

from heatclient.v1.client import Client as HeatClient
from keystoneclient.v2_0 import client as KeystoneClient


TESTSTACKNAME = 'func_test_stack'


def get_keystone_token():
    keystone = KeystoneClient.Client(
        username=USERNAME,
        password=PASSWORD,
        tenant_name=TENANT_NAME,
        auth_url=AUTH_URL
    )
    token = keystone.auth_ref['token']['id']
    return token


def get_heat_client():
    token = get_keystone_token()
    return HeatClient(endpoint=HEAT_ENDPOINT, token=token)


def get_plugins(heat_client):
    return heat_client.resource_types.list()


def get_stack_status(heat_client, stack_id):
    stack = heat_client.stacks.get(stack_id)
    return stack.stack_status


def get_stack(heat_client, stack_id):
    return heat_client.stacks.get(stack_id)


def wait_until_status(
        heat_client,
        stack_id,
        expected_status='create_complete',
        max_tries=10,
        interval=2):
    count = 0
    while count <= max_tries:
        time.sleep(interval)
        status = get_stack_status(heat_client, stack_id)
        if status.lower() == expected_status:
            return True
        count += 1

    return 'Stack {0} still {1} state after max_tries of {1}'.format(
        stack_id, status, str(max_tries)
    )


def create_stack(heat_client, **kwargs):
    name = kwargs['stack_name']
    template = kwargs['template']
    parameters = kwargs.get('parameters', {})
    heat_client.stacks.create(
        stack_name=name,
        template=template,
        files={},
        disable_rollback=True,
        parameters=parameters,
        environment={},
        tags=None,
        environment_files=None
    )
    return heat_client.stacks.get(name)


def delete_stack(heat_client, stack_name):
    heat_client.stacks.delete(stack_name)
    while True:
        try:
            get_stack_status(heat_client, stack_name)
        except Exception as ex:
            if 'could not be found' in str(ex):
                break


def ensure_failed_stack(HeatStack, template, fail_msg):
    hc, stack = HeatStack(template)
    assert wait_until_status(hc, stack.id, 'create_failed') is True
    failed_stack = get_stack(hc, stack.id)
    assert fail_msg in failed_stack.stack_status_reason
    return hc, stack
