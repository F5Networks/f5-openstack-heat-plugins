from f5_heat.resources import f5_sys_iappservice

import mock
import pytest
from f5_heat.resources import f5_sys_iappservice

@pytest.fixture
def F5SysiAppService():
    fake_iapp_service = f5_sys_iappservice.F5SysiAppService("fake_resource", mock.MagicMock(), mock.MagicMock())
    return fake_iapp_service

def test_handle_create(F5SysiAppService):
    F5SysiAppService.handle_create()
    assert 0
