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

import graylog
from graylog.rest import ApiException
from tnglib import env

def get_logs(_from, to, sp_path, filter, file=True):
    # _from = "2019-04-25 17:11:01.201" # Object | Timerange start. See description for date format
    # to = "2019-04-25 17:26:01.201" # Object | Timerange end. See description for date format
    # sp_path = "http://pre-int-sp-ath.5gtango.eu" | Complete url of the SP
    # filter = "source:pre-int-sp-ath* AND container_name:tng-gtk-sp" | Complete filter with Graylogs sintax
    # file = True/False | Write logs to file (Default is True)

    configuration = graylog.Configuration()
    configuration.username = env.graylog_username
    configuration.password = env.graylog_password
    configuration.host = env.graylog_host

    try:
        source = sp_path.split(".")[0].replace("http://","")
    except:
        source = sp_path

    query = "source:{} AND type:E".format(source)

    if filter:
        query = filter

    try:
        # Message search with absolute timerange.
        api_instance = graylog.SearchuniversalabsoluteApi()
        api_response = api_instance.search_absolute(query, _from, to)
        reply = api_response.to_dict()
    except ApiException as e:
        print(e)

    if file:
        with open('graylogs.log', 'w') as logs:
            for message in reply["messages"]:
                logs.write(message["message"]["timestamp"] + " " +
                       message["message"]["container_name"] + ": " +
                       message["message"].get("message") + "\n")
    else:
        for message in reply["messages"]:
            print(message["message"]["timestamp"] + " " + message["message"]["container_name"] + ": " + message["message"].get("message") + "\n")

