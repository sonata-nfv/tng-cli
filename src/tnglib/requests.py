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


def get_requests():
    """Returns info on all requests.


    :returns: A list. [0] is a bool with the result. [1] is a list of
        dictionaries, each containing a request.

    """

    # get current list of requests
    resp = requests.get(env.request_api, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for requests returned with " +
                  (str(resp.status_code)))
        return False, []

    requests_dic = json.loads(resp.text)

    req_res = []
    for req in requests_dic:
        dic = {'request_uuid': req['id'],
               'request_type': req['request_type'],
               'status': req['status'],
               'created_at': req['created_at'],
               'instance_uuid': req['instance_uuid']}

        if dic['instance_uuid'] is None:
            dic['instance_uuid'] = ''

        LOG.debug(str(dic))
        req_res.append(dic)

    return True, req_res


def get_request(request_uuid):
    """Returns info on a specific request.

    :param request_uuid: A string. The uuid of the request.
    :returns: A list. [0] is a bool with the result. [1] is a dictionary
        containing the request.

    """

    # get request info
    resp = requests.get(env.request_api + '/' + request_uuid,
                        timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for request returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)


def service_instantiate(service_uuid, sla_uuid=None):
    """Makes a request to instantiate a service.

    :param service_uuid: A string. The uuid of the service.
    :param sla_uuid: A string (Default value = None). The uuid of the SLA.
    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the instantiated service.

    """
    
    data = {"service_uuid": service_uuid,
            "request_type": "CREATE_SERVICE"}

    if sla_uuid:
        data['sla_id'] = sla_uuid

    return _post_request(data)


def service_terminate(instance_uuid):
    """Makes a request to terminate a service.

    :param instance_uuid: A string. The uuid of the instance.
    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the terminated instance.

    """
    
    data = {"instance_uuid": instance_uuid,
            "request_type": "TERMINATE_SERVICE"}

    return _post_request(data)


def _post_request(data):
    """ Generic request maker. """

    resp = requests.post(env.request_api,
                         json=data,
                         timeout=env.timeout)

    if resp.status_code != 201:
        LOG.debug("Request returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)['id']
