#!/usr/bin/env python

import requests
import collections
import yaml
import re

HOSTS_ENDPOINT = "https://riffraff.gutools.co.uk/api/deployinfo"
CONFIG_PATH = "config.yml"
ALL_STAGES = ["PROD", "PERF", "CODE", "QA", "DEV"]
INTERNAL_NAME_MATCHER = re.compile(r"^(ip[\d-]+)")

class SSHEntry(object):
    def __init__(self, host, host_name, extra_params=dict()):
        self.parts = [("Host", host),
                      ("HostName", host_name)] + extra_params.items()

    def __repr__(self):
        return "\n".join(k + " " + v for k, v in self.parts)

class ExtraParams(object):
    def __init__(self, apps, stages, entries):
        resolver = dict()

        for entry in entries:
            entry_apps = apps if entry["apps"] == "*" else entry["apps"]
            entry_stages = stages if entry["stages"] == "*" else entry["stages"]

            for app in entry_apps:
                for stage in entry_stages:
                    resolver[(app, stage)] = entry["params"]

        self.resolver = resolver

    def params_for(self, app, stage):
        return self.resolver.get((app, stage), dict())

class AppNameGenerator(object):
    def __init__(self, rewrites):
        self.rewrites = rewrites

    def name(self, app, stage, index):
        return self.rewrites.get(app, app) + "_" + stage.lower() + "_" + str(index + 1)

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

def trim_internal_name(name):
    return INTERNAL_NAME_MATCHER.search(name).group(1)

def get_ssh_entries(hosts, namer, extra_params):
    ssh_entries_by_app = collections.defaultdict(list)

    for h in hosts:
        ssh_entries_by_app[(h["app"], h["stage"])].append(h)

    return [entry \
            for (app, stage), hosts in ssh_entries_by_app.items() \
            for i, host in enumerate(hosts)
            for entry in 
            (SSHEntry(namer.name(app, stage, i), \
                      host["hostname"], \
                      extra_params.params_for(app, stage)),
             SSHEntry(trim_internal_name(host["internalname"]), \
                      host["hostname"], \
                      extra_params.params_for(app, stage)))]

def main():
    conf = get_config()

    api_key = conf["api_key"]

    apps = set(conf["apps"])

    hosts = (h for h in get_hosts(api_key) if h["app"] in apps)

    namer = AppNameGenerator(conf.get("app_name_rewrites", dict()))
    extra_params = ExtraParams(apps, ALL_STAGES, conf.get("extra_params", list()))

    ssh_entries = get_ssh_entries(hosts, namer, extra_params)

    try:
        with open(conf.get("static_config_path", "static_config"), "r") as static_conf:
            print static_conf.read()
    except IOError, e: 
        # No static config defined
        pass

    print "# Riff Raff SSH entries"
    print

    for entry in ssh_entries:
        print str(entry)
        print

if __name__ == '__main__':
    main()


