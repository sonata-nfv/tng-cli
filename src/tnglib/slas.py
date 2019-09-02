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


def create_sla_template(templateName, nsd_uuid, expireDate,
                        guaranteeId, service_licence_type,
                        allowed_service_instances,
                        service_licence_expiration_date,
                        template_initiator, provider_name,
                        dflavour_name=None):

    """Generates an initial SLA template.

    :param templateName: name for the SLA template. 
    :param nsd_uuid: uuid of the network service.
    :param expireDate: DD/MM/YYYY expiration date.
    :param guaranteeId: id of the SLA guarantee.
    :param template_initiator: the one who creates the sla template e.g. Uprc.
    :param provider_name: the vendor on behalf of whom the sla template is 
        generated e.g. Telefonica.
    :param dflavour_name: the mapped deployment flavor.
    :param service_licence_type: the selected license 
        type (public|trial|private).
    :param allowed_service_instances: the allowed ns instances based on 
        the license.
    :param service_licence_expiration_date: DD/MM/YYYY license expiration date.

    :returns: A tuple. [0] is a bool with the result. [1] is a string containing
        the uuid of the created SLA template.
    """

    # generate sla template
    data = {'templateName': templateName,
            'nsd_uuid': nsd_uuid,
            'guaranteeId':guaranteeId,
            'expireDate': expireDate,
            'template_initiator': template_initiator,
            'provider_name': provider_name,
            'dflavour_name':dflavour_name,
            'service_licence_type':service_licence_type,
            'allowed_service_instances':allowed_service_instances,
            'service_licence_expiration_date':service_licence_expiration_date}

    resp = requests.post(env.sl_templates_api,
                         data=data,
                         timeout=env.timeout,
                         headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 201:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    uuid = json.loads(resp.text)['uuid']

    return True, uuid


def get_sla_templates():
    """Returns info on all available SLA templates.

    :returns: A tuple. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains an SLA template.
    """

    # get current list of templates
    resp = requests.get(env.sl_templates_api,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    templates = json.loads(resp.text)

    temp_res = []

    for template in templates:
        dic = {'name': template['slad']['name'],
               'created_at': template['created_at'],
               'service': template['slad']['sla_template']['service']['ns_name'],
               'sla_uuid': template['uuid'],
               }
        LOG.debug(str(dic))
        temp_res.append(dic)

    return True, temp_res


def get_sla_template(sla_uuid):
    """Returns info on all available SLA templates.

    :param sla_uuid: uuid of an SLA template.

    :returns: A tuple. [0] is a bool with the result. [1] is a dictionary 
        containg an SLA template.
    """

    # get current list of templates
    url = env.sl_templates_api + '/' + sla_uuid
    resp = requests.get(url, timeout=env.timeout, headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    template = json.loads(resp.text)

    return True, template


def delete_sla_template(sla_template_uuid):
    """Deletes an SLA template.

    :param sla_template_uuid: uuid of an SLA template.

    :returns: A tuple. [0] is a bool with the result. [1] is a string containing
        the uuid of the terminated SLA.
    """

    url = env.sl_templates_api + '/' + sla_template_uuid

    resp = requests.delete(url, timeout=env.timeout, headers=env.header)
    LOG.debug(sla_template_uuid)
    LOG.debug(str(resp.text))

    env.set_return_header(resp.headers)

    if resp.status_code == 200:
        return True, sla_template_uuid
    else:
        return False, json.loads(resp.text)


def get_sla_guarantees():
    """Returns info on all available SLA guarantees.

    :returns: A tuple. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains an SLA guarantee.
    """

    # get current list of templates
    resp = requests.get(env.sl_guarantees_api,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    guarantees = json.loads(resp.text)['guaranteeTerms']

    guar_res = []

    for guarantee in guarantees:
        dic = {'name': guarantee['guarantee_name'],
               'id': guarantee['guaranteeID'],
               'operator': guarantee['guarantee_operator'],
               'value': guarantee['guarantee_threshold']}
        LOG.debug(str(dic))
        guar_res.append(dic)

    return True, guar_res


def get_agreements(nsi_uuid=None):
    """Returns info on all available SLA agreements.

    :param nsi_uuid:  (Default value = None) uuid of a service instance.

    :returns: A tuple. [0] is a bool with the result. [1] is a list of 
        dictonaries. Each dictionary contains an SLA agreement.
    """

    url = env.sl_agreements_api
    if nsi_uuid:
        url = env.sl_agreements_api + '/service/' + nsi_uuid

    # get current list of agreements
    resp = requests.get(url, timeout=env.timeout, headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    if nsi_uuid:
        agreements = json.loads(resp.text)['cust_sla']
    else:
        agreements = json.loads(resp.text)['agreements']

    return True, agreements


def get_detailed_agreement(sla_uuid, nsi_uuid):
    """Returns info on a specific Agreement.

    :param sla_uuid: uuid of an SLA template.
    :param nsi_uuid: uuid of a service instance.

    :returns: A tuple. [0] is a bool with the result. [1] is a dictionary
        containing details on a single SLA agreement.
    """
    url = env.sl_agreements_api + '/' + sla_uuid + '/' + nsi_uuid

    resp = requests.get(url, timeout=env.timeout, headers=env.header)
    LOG.debug("SLA UUID: " + sla_uuid + "NSI UUID: " + nsi_uuid)
    LOG.debug(str(resp.text))

    env.set_return_header(resp.headers)

    if resp.status_code == 200:
        return True, json.loads(resp.text)
    else:
        return False, json.loads(resp.text)['error']


def get_violations(nsi_uuid=None):
    """Returns info on all SLA violations.

    :param nsi_uuid:  (Default value = None) uuid of a service instance.

    :returns: A tuple. [0] is a bool with the result. [1] is a list of 
        SLA violations associated to a service instance.
    """

    url = env.sl_violations_api
    if nsi_uuid:
        url = env.sl_violations_api + '/service/' + nsi_uuid

    # get current list of violations
    resp = requests.get(url, timeout=env.timeout, headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    violations = json.loads(resp.text)
    return True, violations


def get_violations_per_nsi_sla(sla_uuid, nsi_uuid):
    """Returns the vaiolations for a specific SLA.

    :param sla_uuid: uuid of SLA template.
    :param nsi_uuid: uuid of network service instance.

    :returns: A tuple. [0] is a bool with the result. [1] is a list of 
        SLA violations associated to a service instance and an SLA 
        template.
    """

    url = env.sl_violations_api + '/' + sla_uuid + '/' + nsi_uuid

    # get current list of violations
    resp = requests.get(url, timeout=env.timeout, headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    violations = json.loads(resp.text)

    return True, violations
