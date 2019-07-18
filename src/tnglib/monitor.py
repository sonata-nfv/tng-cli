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

def get_prometheus_targets():
    """
    Returns all the monitoring targets from Prometheus server.

    """

    # get current list of targets
    resp = requests.get(env.monitor_api+'/prometheus/targets',
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.text)))
        error = "Request returned with " + str(resp.status_code)
        return False, error

    templates = json.loads(resp.text)

    temp_res = []
    if 'targets' in templates:
        for template in templates['targets']:
            if 'job_name' in template:
                trg_name = template['job_name']
            else:
                trg_name = 'null'
            if 'static_configs' in template:
                edpts = ''
                for trg in template['static_configs']:
                    if 'targets' in trg:
                        first_trg = True
                        for e in trg['targets']:
                            if not first_trg:
                                trg_name = ' '
                            dic = {'target': trg_name, 'endpoint': e}
                            first_trg = True
                            LOG.debug(str(dic))
                            temp_res.append(dic)
        return True, temp_res
    else:
        LOG.debug("Request returned with " + (json.dumps(templates)))
        error = "VNFs not found"
        return False, error

def get_services(srv_uuid):
    """
    Returns all the vnfs/vdus per NS.

    """
    # get current list of targets
    resp = requests.get(env.monitor_api+'/services/'+srv_uuid+'/metrics',
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.text)))
        error = "Request returned with " + str(resp.status_code)
        return False, error

    templates = json.loads(resp.text)

    temp_res = []
    if 'vnfs' in templates:
        for template in templates['vnfs']:
            first_vdu = True
            if 'vnf_id' in template:
                vnf_id = template['vnf_id']
            else:
                vnf_id = 'null'
            if 'vdus' in template:
                vdu_ids = ''
                for vdus in template['vdus']:
                    if 'vdu_id' in vdus:
                        if not first_vdu:
                            vnf_id = ' '
                        dic = {'vnf_uuid': vnf_id,
                               'vdu_uuid': vdus['vdu_id']
                            }
                        first_vdu = False
                        LOG.debug(str(dic))
                        temp_res.append(dic)
        return True, temp_res
    else:
        LOG.debug("Request returned with " + (json.dumps(templates)))
        error = "VNFs not found"
        return False, error


def get_metrics(vnf_uuid, vdu_uuid):
    """
    Returns all metrics per vnf and vdu.

    """
    resp=requests.get(env.monitor_api+'/vnfs/'+vnf_uuid+
                        '/vdu/'+vdu_uuid+'/metrics',
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.text)))
        error = "Request returned with " + str(resp.status_code)
        return False, error

    templates = json.loads(resp.text)

    temp_res = []

    if 'vdus' in templates:
        for template in templates['vdus']:
            if 'metrics' in template:
                for mtr in template['metrics']:
                        dic = {'metric_name': mtr['__name__']
                               }
                        LOG.debug(str(dic))
                        if not dic in temp_res:
                            temp_res.append(dic)

        return True, temp_res
    else:
        LOG.debug("Request returned with " + (json.dumps(templates)))
        error = "VDUs not found"
        return False, error

def get_metric(metric_name):
    """
    Returns value per metric name.

    """
    resp=requests.get(env.monitor_api+'/prometheus/metrics/name/'+metric_name,
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    templates = json.loads(resp.text)

    temp_res = []

    if 'metrics' in templates and  'result' in templates['metrics']:
        for res in templates['metrics']['result']:
            dic = {'job': res['metric']['job'],
                   'instance': res['metric']['instance'],
                   'value': res['value'][1]
                    }
            LOG.debug(str(dic))
            if not dic in temp_res:
                temp_res.append(dic)

        return True, temp_res
    else:
        LOG.debug("Request returned with " + (json.dumps(templates)))
        error = "VDUs not found"
        return False, error

def get_vnv_tests(test_uuid):
    """
        Returns list of stored tests.

    """

    if test_uuid:
        resp = requests.get(env.monitor_api + 
            '/api/v2/passive-monitoring-tests/test/' + 
            test_uuid +'?limit=5000',
                            timeout=env.timeout,
                            headers=env.header)
    else:
        resp = requests.get(env.monitor_api + 
            '/api/v2/passive-monitoring-tests?limit=5000',
                            timeout=env.timeout,
                            headers=env.header)


    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = 'This command is available only on VnV platform ('+ 
                (str(resp.status_code)) +')'
        return False, error

    templates = json.loads(resp.text)

    temp_res = []

    if 'results' in templates:
        for res in templates['results']:
            dic = {'test_uuid': res['test_id'], 
                   'srv_uuid': res['service_id'],
                   'started': res['created'], 
                   'terminated':res['terminated']
                   }
            if 'data' in res:
                dic['data'] = res['data']
            LOG.debug(str(dic))
            if not dic in temp_res:
                temp_res.append(dic)

        return True, temp_res
    else:
        LOG.debug("Request returned with " + (json.dumps(templates)))
        error = "Stored test data not found"
        return False, error