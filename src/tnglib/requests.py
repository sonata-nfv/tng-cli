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
    resp = requests.get(env.request_api,
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request for requests returned with " +
                  (str(resp.status_code)))
        LOG.debug(str(resp.text))
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
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request for request returned with " +
                  (str(resp.status_code)))
        LOG.debug(str(resp.text))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)


def service_instantiate(service_uuid, sla_uuid=None, mapping=None):
    """Makes a request to instantiate a service.

    :param service_uuid: A string. The uuid of the service.
    :param sla_uuid: A string (Default value = None). The uuid of the SLA.
    :param input_mapping: dictionary with two keys: vnfs and vls. Both keys
        contain a list. vnf list elements are dictionaries with two keys: vnf_id
        and vim_id. vls list elements are dictionaries with three keys: vl_id,
        external_net and vim_id.
        ---
        network_functions:
          - vnf_id: <foo>
            vim_id: <bar>
          - vnf_id: <foo2>
            vim_id: <bar2>
        virtual_links:
          - vl_id: <foo>
            vim_id: <bar>
            external_net: <foo.bar>
          - vl_id: <foo2>
            vim_id: <bar2>
            external_net: <foo.bar2>
    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the instantiated service.

    """
    
    data = {"service_uuid": service_uuid,
            "request_type": "CREATE_SERVICE"}

    if sla_uuid:
        data['sla_id'] = sla_uuid

    if mapping:
        data['mapping'] = mapping

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


def slice_instantiate(slice_template_uuid, name=None, description=None):
    """Makes a request to instantiate a slice.

    :param slice_template_uuid: A string. The uuid of the slice template.
    :param name: A string (Default value = None). A name for the slice 
        instance.
    :param description: A string (Default value = None). A description 
        for the slice template
    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the instantiated slice.

    """
    
    data = {"nst_id": slice_template_uuid,
            "request_type": "CREATE_SLICE"}

    if name:
        data['name'] = name
    else:
        data['name'] = 'foobar'

    if description:
        data['description'] = description
    else:
        data['description'] = 'foobar'

    return _post_request(data)


def slice_terminate(instance_uuid):
    """Makes a request to terminate a slice.

    :param instance_uuid: A string. The uuid of the slice instance.
    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the terminated slice instance.

    """
    
    data = {"instance_uuid": instance_uuid,
            "request_type": "TERMINATE_SLICE"}

    return _post_request(data)

def service_scale_out(instance_uuid, vnfd_uuid, number_inst=1, vim_uuid=None):
    """
    Makes a request to scale out a service.

    :param instance_uuid: A string. The uuid of the service instance.
    :param vnfd_uuid: A string. the uuid of the vnf descriptor to scale.
    :param number_inst: An integer. Number of required extra intances.
    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the request.

    """

    if not number_inst:
        number_inst = 1

    data = {"instance_uuid": instance_uuid,
            "request_type": "SCALE_SERVICE",
            "scaling_type": "ADD_VNF",
            "vnfd_uuid": vnfd_uuid,
            "number_of_instances": number_inst
            }

    if vim_uuid:
        data["vim_uuid"] = vim_uuid

    return _post_request(data)

def service_scale_in(instance_uuid, vnf_uuid=None, vnfd_uuid=None, number_inst=1):
    """
    Makes a request to scale in a service.

    :param instance_uuid: A string. The uuid of the service instance.
    :param vnfd_uuid: A string. the uuid of either the vnf descriptor or instance
        that needs to be scaled in.
    :param vnf_uuid: A string. Contains the uuid of a VNF instance.
    :param number_inst: An integer. Number of required intances to scale in.
        Only when vnfd_uuid is present.
    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the request.

    """
    if not number_inst:
        number_inst = 1

    data = {
            "instance_uuid": instance_uuid,
            "request_type": "SCALE_SERVICE",
            "scaling_type": "REMOVE_VNF",
        }

    if vnf_uuid:
        data["vnf_uuid"] = vnf_uuid

    elif vnfd_uuid:
        data["vnfd_uuid"] = vnfd_uuid
        data["number_of_instances"] = number_inst

    return _post_request(data)

def _post_request(data):
    """ Generic request maker. """

    resp = requests.post(env.request_api,
                         json=data,
                         timeout=env.timeout,
                         headers=env.header)

    if resp.status_code != 201:
        LOG.debug("Request returned with " +
                  (str(resp.status_code)))
        LOG.debug(str(resp.text))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)['id']
