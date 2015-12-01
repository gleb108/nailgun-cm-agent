#!/usr/bin/env python


import argparse
import os
import sys
import yaml
import time
from fuelclient.cli.error import DeployProgressError
from fuelclient.objects import *

#parsing CLI arguments       
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action="store_true", default=False, dest="verbose", help="Enable verbose mode")
parser.add_argument('-c', '--config', action="store", default="./nailgun-cm-agent.yaml", dest="config", help="Config file")

args = parser.parse_args()

#Getting Configuration
with open(args.config, 'r') as settings:
    cfg = yaml.load(settings)
    if args.verbose:
       print  "Using config {0}".format(args.config)

env_id = cfg['env-id']
path = cfg['puppet-modules']

roles = cfg['roles']
if args.verbose:
   print "\nRoles:"
   for r in roles:
       print r

start_task = cfg['default_start_task']
if args.verbose:
   print "\nstart_task: {0}".format(start_task)
end_task = cfg['default_end_task']
if args.verbose:
   print "\nend_task: {0}".format(end_task)

skip_tasks = cfg['skip-tasks']
if args.verbose:
   print "\nTasks to skip:"
   for t in skip_tasks:
       print t

def ok_to_run ():
    nodes = Node.get_all_data()
    for node in nodes:
        if node['status'] == 'Deploying':
           return False
    return True



def get_nodes ():
    nodes = Node.get_all_data()
    res = {}
    for node in nodes:
        if node['cluster'] == env_id and node['online']:
           res[node['id']] = node['roles']
    return res

def run (nodes, tasks):
    node_collection = NodeCollection.init_with_ids(nodes)
    run = env.execute_tasks(node_collection,tasks)
    if not ok_to_run():
       sys.exit(1)
    while True:
       if args.verbose:
          print "Progress: {0} Status: {1}".format(run.progress, run.status)
       if run.progress == 100 or run.status == 'error':
          break
       time.sleep(1)



env = Environment(env_id)

# get_tasks(self, skip=None, end=None, start=None, include=None)
#     Stores logic to filter tasks by known parameters.
#     
#     :param skip: list of tasks or None
#     :param end: string or None
#     :param start: string or None
#     :param include: list or None
tasks = env.get_tasks(skip_tasks,end_task, start_task, None)
if args.verbose:
   print "\nTasks to execute:" 
   for t in tasks:
       print t

nodes = get_nodes()
controllers = []
other_nodes =  []
for node_id in nodes.keys():
    roles= nodes[node_id]
    if roles.count('controller'):
       controllers.append(node_id)
    else:
       other_nodes.append(node_id)

if args.verbose:
   print "\nController nodes: {0}".format(controllers)
run(controllers, tasks)


if args.verbose:
   print "\nOther nodes: {0}".format(other_nodes) 
run(other_nodes, tasks)





