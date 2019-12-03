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

def add_prometheus_targets(name, endpoint, type, path):
    """Adds a new monitoring endpoint.
    k8s ex. monitor -tra --target-name test1 --target-type k8s --target-endpoint 10.200.16.2:30090 --target-path /federate
    Exporter ex. monitor -tra --target-name test1 --target-type exporter --target-endpoint 145.20.146.2:9091 --target-path /metrics

    :param name: name of the monitored VIM.
    :param endpoint: monitoring endpoint (<IP>:<PORT>).
    :param type: type of exporter ('k8s' or 'exporter').
    :param path: url's path ('/federate' or 'metrics').
    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a target.
    """
    # get current list of targets
    resp = requests.get(env.monitor_api + '/prometheus/targets',
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    templates = json.loads(resp.text)

    if type == 'k8s':
        trg = {'honor_labels':True,'job_name':name,'metrics_path':path,
               'params':{'match':["{job='kubernetes-cadvisor'}",
                                  "{job='kubernetes-apiservers'}",
                                  "{job='kubernetes-nodes'}",
                                  "{job='kubernetes-pods'}",
                                  "{job='kubernetes-service-endpoints'}",
                                  "{job='pushgateway'}"]},
               'scrape_interval':'10s','scrape_timeout':'10s',
               'static_configs':[{'targets':[endpoint]}]}
    elif type == 'exporter':
        trg = {'job_name': name, 'metrics_path':path,
               'scrape_interval':"5s",
               'scrape_timeout': "5s",
               'static_configs': [{'targets': [endpoint]}]}
    else:
        LOG.debug("Provide exporter type (k8s/exporter)")
        error = "Unsupported exporter type (k8s/exporter)"
        return False, error

    found = False
    if 'targets' in templates:
        i = 0
        for t in templates['targets']:
            if 'job_name' in t:
                if ':' in t['job_name']:
                    trg_name = t['job_name'].split(':')[0]
                else:
                    trg_name = t['job_name']
                if trg_name == name:
                    templates['targets'][i] = trg
                    found = True
                    break
            i =i + 1

        if not found:
            templates['targets'].append(trg)

    resp = requests.post(env.monitor_api + '/prometheus/targets',
                         json=templates,
                         timeout=env.timeout,
                         headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    return True, get_prometheus_targets()[1]

def get_prometheus_targets():
    """Returns all the monitoring targets from Prometheus server.

    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a target.
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
                            if ':' in trg_name:
                                trg_name = trg_name.split(':')[0]
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
    """Returns all the vnfs/vdus per NS.

    :param srv_uuid: uuid of a network service record.
    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a vdu per vnf.
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
    """Returns all metrics per vnf and vdu.
    :param vnf_uuid: uuid of a vnf record.
    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a metric per vdu/vnf.

    """
    resp=requests.get(env.monitor_api+'/vnfs/'+vnf_uuid + \
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
    
def get_policy_rules(nsr_id):
    """Returns the number of activate policy monitoring rules.

    :param nsr_id: uuid of a network service record.

    :returns: A tuple. [0] is a bool with the result. [1] the number of rules.
    """

    # get policy monitoring rules
    url = env.monitoring_manager_api + '/policies/monitoring-rules/service/' + nsr_id
    
    resp = requests.get(url, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for monitoring policy rule returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)
    
    num_of_rules = json.loads(resp.text)['count']

    return True, str(num_of_rules)

def get_metric(metric_name):
    """Returns value per metric name.

    :param metric_name: name of the metric.
    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a metric.
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

def stop_monitoring(service_uuid):
    """Stop collecting data related to specific service.
    :param service_uuid: uuid of a network service record.
    :returns: A list. [0] is a bool with the result.
    """
    url = env.monitor_api+'/services/'+ \
                        service_uuid
    resp = requests.delete(url,
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    temp_res = []
    temp_res.append({'srv_uuid': service_uuid})

    return True, temp_res


def get_vnv_tests(service_uuid):
    """ Returns list of stored tests. 
    :param service_uuid: uuid of a network service record.
    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains VnV test.

    """

    if service_uuid:
        resp = requests.get(env.monitor_api + \
            '/passive-monitoring-tests/service/' + \
            service_uuid,
                            timeout=env.timeout,
                            headers=env.header)
    else:
        resp = requests.get(env.monitor_api + \
            '/passive-monitoring-tests?limit=5000',
                            timeout=env.timeout,
                            headers=env.header)


    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = 'This command is available only on VnV platform ('+ \
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