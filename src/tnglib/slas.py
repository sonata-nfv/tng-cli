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

def create_template():

	return True
	
def get_sla_templates():
    """
    This function returns info on all available SLA templates
    """

    # get current list of templates
    resp = requests.get(env.sl_templates_api, timeout=5.0)

    if resp.status_code != 200:
        LOG.debug("Request for sla templates returned with " + (str(resp.status_code)))
        return False, []

    templates = json.loads(resp.text)

    return True, templates
	
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
        return False, json.loads(resp.text)['error']
	
def get_agreements():

	return True