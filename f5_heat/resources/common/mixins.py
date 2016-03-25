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


def f5_common_resources(func):
    def func_wrapper(self, *args, **kwargs):
        self.get_bigip()
        self.set_partition_name()
        return func(self, *args, **kwargs)
    return func_wrapper


def f5_bigip(func):
    def func_wrapper(self, *args, **kwargs):
        self.get_bigip()
        func(self, *args, **kwargs)
    return func_wrapper


class F5BigIPMixin(object):
    '''This class is to be subclassed by an F5® Heat Resource Plugin.'''

    def get_bigip(self):
        '''Retrieve the BIG-IP® connection from the F5::BigIP resource.'''

        refid = self.properties[self.BIGIP_SERVER]
        self.bigip = self.stack.resource_by_refid(refid).get_bigip()

    def set_partition_name(self):
        '''Return the partition name from the F5::Sys::Partition resource.

        :returns: string partition name
        '''

        refid = self.properties[self.PARTITION]
        self.partition_name = \
            self.stack.resource_by_refid(refid).get_partition_name()
