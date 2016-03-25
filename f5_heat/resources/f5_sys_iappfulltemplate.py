# coding=utf-8
#
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

from heat.common import exception
from heat.common.i18n import _
from heat.engine import properties
from heat.engine import resource

from common.mixins import f5_common_resources
from common.mixins import F5BigIPMixin
from f5.common.iapp_parser import IappParser


class IappFullTemplateValidationFailed(exception.StackValidationFailed):
    pass


class F5SysiAppFullTemplate(F5BigIPMixin, resource.Resource):
    '''Manages creation of an iApp® resource on the BIG-IP®.'''

    PROPERTIES = (
        BIGIP_SERVER,
        PARTITION,
        FULL_TEMPLATE
    ) = (
        'bigip_server',
        'partition',
        'full_template'
    )

    properties_schema = {
        BIGIP_SERVER: properties.Schema(
            properties.Schema.STRING,
            _('BigIP resource reference.'),
            required=True
        ),
        PARTITION: properties.Schema(
            properties.Schema.STRING,
            _('Partition resource reference.'),
            required=True
        ),
        FULL_TEMPLATE: properties.Schema(
            properties.Schema.STRING,
            _('Full iapp template string.'),
            required=True
        )
    }

    def __init__(self, name, defn, stack):
        super(F5SysiAppFullTemplate, self).__init__(name, defn, stack)
        self._parse_full_template()

    def _parse_full_template(self):
        '''Parse full template and set resulting dictionary as instance attr.

        '''

        templ = self.properties[self.FULL_TEMPLATE]
        self.template_dict = IappParser(templ).parse_template()

    @f5_common_resources
    def _validate_template_partition(self):
        try:
            assert self.template_dict['partition'] == self.partition_name
        except AssertionError:
            message = _('The partition defined in the iapp template does not '
                        'match the partition given in the yaml configuration.'
                        ' Please ensure these match')
            raise IappFullTemplateValidationFailed(message)

    @f5_common_resources
    def handle_create(self):
        '''Create the template on the BIG-IP®.

        :raises: ResourceFailure
        '''

        self._validate_template_partition()
        try:
            template = self.bigip.sys.applications.templates.template
            template.create(**self.template_dict)
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    @f5_common_resources
    def handle_delete(self):
        '''Delete the iApp® Template on the BIG-IP®.

        :raises: ResourceFailure
        '''

        if self.bigip.sys.applications.templates.template.exists(
                name=self.template_dict['name'],
                partition=self.partition_name
        ):
            try:
                loaded_template = self.bigip.sys.applications.templates.template.\
                    load(
                        name=self.template_dict['name'],
                        partition=self.partition_name
                    )
                loaded_template.delete()
            except Exception as ex:
                raise exception.ResourceFailure(ex, None, action='DELETE')
        return True


def resource_mapping():
    return {'F5::Sys::iAppFullTemplate': F5SysiAppFullTemplate}
