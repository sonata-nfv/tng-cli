# Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).
#
# This work has been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the 5GTANGO
# partner consortium (www.5gtango.eu).

import requests
import logging
import json
import time
import os
import yaml
import tnglib.env as env

LOG = logging.getLogger(__name__)


def get_function_descriptors():
    """Returns info on all available function descriptors.

    :returns: A tuple. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a descriptor.
    """

    # get current list of function descriptors
    resp = requests.get(env.function_descriptor_api,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for function descriptors returned with " +
                  (str(resp.status_code)))
        return False, []

    functions = json.loads(resp.text)

    functions_res = []
    for function in functions:
        if function['platform'] == 'osm':
            continue
        dic = {'descriptor_uuid': function['uuid'],
               'name': function['vnfd']['name'],
               'version': function['vnfd']['version'],
               'created_at': function['created_at']}
        LOG.debug(str(dic))
        functions_res.append(dic)

    return True, functions_res


def get_function_descriptor(function_descriptor_uuid):
    """Returns info on a specific function descriptor.

    :param function_descriptor_uuid: uuid of the vnfd.

    :returns: A tuple. [0] is a bool with the result. [1] is a dictionary 
        containing the vnfd.
    """

    # get function descriptor
    url = env.function_descriptor_api + '/' + function_descriptor_uuid
    resp = requests.get(url,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for function descriptor returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)


def get_function_instances():
    """Returns info on all available function instances.

    :returns: A tuple. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a vnfr.
    """

    # get current list of function instances
    resp = requests.get(env.function_instance_api,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for function instances returned with " +
                  (str(resp.status_code)))
        return False, []

    functions = json.loads(resp.text)

    functions_res = []
    for function in functions:
        dic = {'instance_uuid': function['uuid'],
               'status': function['status'],
               'version': function['version'],
               'created_at': function['created_at']}
        LOG.debug(str(dic))
        functions_res.append(dic)

    return True, functions_res


def get_function_instance(function_instance_uuid):
    """Returns info on a specific function instance.

    :param function_instance_uuid: uuid of the vnfr.

    :returns: A tuple. [0] is a bool with the result. [1] is a dictionary 
        containing a vnfr.
    """

    # get function intsance info
    url = env.function_instance_api + '/' + function_instance_uuid
    resp = requests.get(url,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for function instance returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)
