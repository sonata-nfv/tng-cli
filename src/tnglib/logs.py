#!/usr/bin/python3
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

