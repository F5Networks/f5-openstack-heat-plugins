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

from heatclient.exc import HTTPException

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def test_create_complete(HeatStack):
    hc, stack = HeatStack(os.path.join(TEST_DIR, 'success.yaml'))
    assert hc.wait_until_status(stack.id, 'create_complete') is True


def test_create_failed_bad_ip(HeatStackNoParams):
    with pytest.raises(HTTPException) as ex:
        HeatStackNoParams(os.path.join(TEST_DIR, 'bad_ip.yaml'))
    # The below messages could exist depending in the testers version of the
    # openstack heat engine. The suffix of the variable signifies the engine
    # version
    msg_engine_2015_1_2 = 'Failed to initialize BigIP object'
    msg_engine_2015_1_3 = 'Failed to establish a new connection'
    if msg_engine_2015_1_2 not in ex.value.message and \
            msg_engine_2015_1_3 not in ex.value.message:
        pytest.fail('Neither of the following messages were found in the '
                    'exception from the Heat engine to the client: %s\n\n%s' %
                    (msg_engine_2015_1_2, msg_engine_2015_1_3))


def test_create_failed_bad_password(HeatStack):
    with pytest.raises(HTTPException) as ex:
        HeatStack(os.path.join(TEST_DIR, 'bad_password.yaml'))
    msg = 'F5 Authorization Required for uri'
    assert msg in ex.value.message


def test_create_bad_property(HeatStack):
    with pytest.raises(HTTPException) as ex:
        HeatStack(os.path.join(TEST_DIR, 'bad_property.yaml'))
    assert 'Unknown Property bad_extra_prop' in ex.value.message
