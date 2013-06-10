#!/usr/bin/env python

import requests
import collections
import yaml

HOSTS_ENDPOINT = "https://dev.riffraff.gudev.gnl/api/deployinfo"
CONFIG_PATH = "config.yml"

class SSHEntry(object):
    def __init__(self, host, host_name):
        self.parts = (("Host", host),
                      ("HostName", host_name))

    def __repr__(self):
        return "\n".join(k + " " + v for k, v in self.parts)

class RiffRaffError(Exception): pass

def get_config():
    return yaml.load(open(CONFIG_PATH, "r"))

def get_hosts(key):
    # Riff Raff does not have a valid SSH certificate at the time of writing
    # this
    response = requests.get(HOSTS_ENDPOINT, params=dict(key=key), \
                            verify=False)
    if response.status_code != 200:
        raise RiffRaffError("Riff Raff returned %d error" % response.status_code)
    else:
        return response.json()["response"]["results"]["hosts"]

def get_ssh_entries(hosts, app_name_rewrites):
    ssh_entries_by_app = collections.defaultdict(list)

    for h in hosts:
        ssh_entries_by_app[(h["app"], h["stage"])].append(h)

    return [SSHEntry(app_name_rewrites.get(app, app) + "_" + \
                     stage.lower() + "_" + str(i + 1), host["hostname"]) \
            for (app, stage), hosts in ssh_entries_by_app.items() \
            for i, host in enumerate(hosts)]

def main():
    conf = get_config()

    api_key = conf["api_key"]

    apps = set(conf["apps"])

    hosts = (h for h in get_hosts(api_key) if h["app"] in apps)

    ssh_entries = get_ssh_entries(hosts, conf.get("app_name_rewrites", dict()))

    for entry in ssh_entries:
        print str(entry)

if __name__ == '__main__':
    main()


