#!/usr/bin/env python

import requests
import collections

HOSTS_ENDPOINT = "https://dev.riffraff.gudev.gnl/api/deployinfo"

apps = {"mobile-aggregator", "mobile_aggregator::frontend"}
hostname_rewrites = {"mobile-aggregator": "ma",
                     "mobile_aggregator::frontend": "ma_squid"}

class SSHEntry(object):
    def __init__(self, host, host_name):
        self.parts = (("Host", self.host),
                      ("HostName", self.host_name))

    def __repr__(self):
        return "\n".join(k + " " + v for k, v in parts)

def get_hosts(key):
    # Riff Raff does not have a valid SSH certificate at the time of writing this
    json = requests.get(HOSTS_ENDPOINT, params=dict(key=key), verify=False).json()
    return json["response"]["results"]["hosts"]

def process():
    api_key = "insert api key here"

    host_details = (h for h in get_hosts(api_key) if h["app"] in apps)

    ssh_entries_by_app = collections.defaultdict(list)

    for h in host_details:
        ssh_entries_by_app[(h["app"], h["stage"])].append(h)

    ssh_entries = [SSHEntry(hostname_rewrites.get(app, app) + "_" + \
                            stage.lower() + "_" + str(i + 1), host["hostname"]) \
                   for (app, stage), hosts in ssh_entries_by_app.items() \
                   for i, host in enumerate(hosts)]

    for entry in ssh_entries:
        print str(entry)

def main():
    process()

if __name__ == '__main__':
    main()


