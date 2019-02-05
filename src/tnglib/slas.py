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

def create_sla_template(templateName,nsd_uuid,expireDate,guaranteeId):
    """
    This function generates an initial SLA template
    """
    # generate sla template
    resp = requests.post(env.sl_templates_api,
                         data = {'templateName':templateName,'nsd_uuid':nsd_uuid,'expireDate':expireDate,'guaranteeId':guaranteeId},
                         timeout=5.0)
	
    if resp.status_code != 201:
        LOG.debug("Request for creating sla templates returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    uuid = json.loads(resp.text)['uuid']

    return True, uuid
	
def get_sla_templates():
    """
    This function returns info on all available SLA templates
    """

    # get current list of templates
    resp = requests.get(env.sl_templates_api, timeout=5.0)

    if resp.status_code != 200:
        LOG.debug("Request for sla templates returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    templates = json.loads(resp.text)

    temp_res = []

    for template in templates:
        dic = {'name': template['slad']['name'],
               'created_at': template['created_at'],
               'sla_uuid': template['uuid'],
               }
        LOG.debug(str(dic))
        temp_res.append(dic)

    return True, temp_res

def get_sla_template(sla_uuid):
    """
    This function returns info on all available SLA templates
    """

    # get current list of templates
    resp = requests.get(env.sl_templates_api + '/' + sla_uuid, timeout=5.0)

    if resp.status_code != 200:
        LOG.debug("Request for sla template returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    template = json.loads(resp.text)

    return True, template
	
def delete_sla_template(sla_template_uuid):
    """
    This function deletes a SLA template
    """

    url = env.sl_templates_api + '/' + sla_template_uuid

    resp = requests.delete(url, timeout=5.0)
    LOG.debug(sla_template_uuid)
    LOG.debug(str(resp.text))

    if resp.status_code == 200:
        return True, sla_template_uuid
    else:
        return False

def get_sla_guarantees():
    """
    This function returns info on all available SLA guarantees
    """

    # get current list of templates
    resp = requests.get(env.sl_guarantees_api, timeout=5.0)

    if resp.status_code != 200:
        LOG.debug("Request for sla guarantees returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    guarantees = json.loads(resp.text)['guaranteeTerms']

    guar_res = []

    for guarantee in guarantees:
        dic = {'name': guarantee['name'],
               'id': guarantee['guaranteeID'],
               'operator': guarantee['operator'],
               'value' : guarantee['value']}
        LOG.debug(str(dic))
        guar_res.append(dic)

    return True, guar_res

def get_agreements(nsi_uuid=None):
    """
    This function returns info on all available SLA agreements
    """

    url = env.sl_agreements_api
    if nsi_uuid:
        url = env.sl_agreements_api + '/service/' + nsi_uuid

    # get current list of agreements
    resp = requests.get(url, timeout=5.0)

    if resp.status_code != 200:
        LOG.debug("Request for sla agreements returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    if nsi_uuid:
        agreements = json.loads(resp.text)['cust_sla']
    else:
        agreements = json.loads(resp.text)['agreements']

    return True, agreements
	
def get_detailed_agreement(sla_uuid,nsi_uuid):
    """
    This function returns info on a specific Agreement
    """
    url = env.sl_agreements_api + '/' + sla_uuid + '/' + nsi_uuid

    resp = requests.get(url, timeout=5.0)
    LOG.debug("SLA UUID: " + sla_uuid + "NSI UUID: " + nsi_uuid)
    LOG.debug(str(resp.text))

    if resp.status_code == 200:
        return True, json.loads(resp.text)
    else:
        return False, json.loads(resp.text)['error']
	
def get_violations(nsi_uuid=None):
    """
    This function returns info on all SLA violations
    """

    url = env.sl_violations_api
    if nsi_uuid:
        url = env.sl_violations_api + '/service/' + nsi_uuid

    # get current list of violations
    resp = requests.get(url, timeout=5.0)

    if resp.status_code != 200:
        LOG.debug("Request for sla violations returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    violations = json.loads(resp.text)
    return True, violations		
	
def get_violations_per_nsi_sla(sla_uuid,nsi_uuid):
    """
    This function returns the vaiolations for a specific SLA
    """
	
    url = env.sl_violations_api + '/' + sla_uuid + '/' + nsi_uuid

    # get current list of violations
    resp = requests.get(url, timeout=5.0)

    if resp.status_code != 200:
        LOG.debug("Request for sla violations returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    violations = json.loads(resp.text)

    return True, violations			