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

# Commons
timeout = 15.0

# Building all paths for global use
sp_path = ''
root_api = ''
user_api = ''
session_api = ''
pkg_api = ''
pkg_status_api = ''
request_api = ''
service_descriptor_api = ''
service_instance_api = ''
function_descriptor_api = ''
function_instance_api = ''
sl_templates_api = ''
sl_agreements_api = ''
sl_violations_api = ''
sl_guarantees_api = ''
slice_template_api = ''
slice_instance_api = ''
policy_api = ''
policy_bind_api = ''
test_results_api = ''
monitor_api = ''
recommendations_api = ''
graylog_username = "api"
graylog_password = "apiapi"
graylog_host = "logs.sonata-nfv.eu:12900"
header = {}
return_header = {}

def get_return_header():
    """
    Return the header of the last curl response.

    :returns: dictionary containg header of last curl response.
    """

    return return_header

def set_return_header(header):
    """
    Store the header of the last curl response.

    :param header: the header to store
    """

    global return_header
    return_header = header

def get_sp_path():
    """Get the configured SP url.

    :returns: the SP url.
    """

    return sp_path

def set_timeout(timeout_in):
    """Set the timeout.

    :param timeout_in: new request timeout
    """

    global timeout
    timeout = timeout_in

def set_sp_path(new_base_path):
    """Set the path were the SP can be reached.

    :param new_base_path: SP url
    """

    global sp_path
    sp_path = new_base_path
    _build_paths()

def add_token_to_header(token):
    """Set the header for all requests with the token.

    :param token: the token
    """

    global header
    header = {'Authorization': 'Bearer ' + token}

def _build_paths():
    """ """

    global root_api
    global pkg_api
    global session_api
    global user_api
    global pkg_status_api
    global request_api
    global service_descriptor_api
    global service_instance_api
    global function_descriptor_api
    global function_instance_api
    global sl_templates_api
    global sl_agreements_api
    global sl_violations_api
    global sl_guarantees_api
    global slice_template_api
    global slice_instance_api
    global policy_api
    global policy_bind_api
    global test_results_api
    global test_plans_api
    global test_descriptors_api
    global monitor_api
    global recommendations_api

    gtk_api = ":32002/api/v3"
    root_api = sp_path + gtk_api
    user_api = sp_path + gtk_api + '/users'
    session_api = sp_path + gtk_api + "/users/sessions"
    pkg_api = sp_path + gtk_api + "/packages"
    pkg_status_api = pkg_api + "/status"
    request_api = sp_path + gtk_api + "/requests"
    service_descriptor_api = sp_path + gtk_api + "/services"
    service_instance_api = sp_path + gtk_api + "/records/services"
    function_descriptor_api = sp_path + gtk_api + "/functions"
    function_instance_api = sp_path + gtk_api + "/records/functions"
    sl_templates_api = sp_path + gtk_api + "/slas/templates"
    sl_agreements_api = sp_path + gtk_api + "/slas/agreements"
    sl_violations_api = sp_path + gtk_api + "/slas/violations"
    sl_guarantees_api = sp_path + gtk_api + "/slas/configurations/guaranteesList"
    slice_template_api = sp_path + gtk_api + "/slices"
    slice_instance_api = sp_path + gtk_api + "/slice-instances"
    policy_api = sp_path + gtk_api + "/policies"
    policy_bind_api = sp_path + gtk_api + "/policies/bind"
    test_results_api = sp_path + gtk_api + "/tests/results"
    test_plans_api = sp_path + gtk_api + "/tests/plans"
    test_descriptors_api = sp_path + gtk_api + "/tests/descriptors"
    monitor_api = sp_path + gtk_api + "/monitoring/data"
    recommendations_api = sp_path + gtk_api + "/recommendations"