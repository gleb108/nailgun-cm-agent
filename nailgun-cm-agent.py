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
start_task = cfg['default_start_task']
end_task = cfg['default_end_task']

skip_tasks = cfg['skip-tasks']
if args.verbose:
   print
   print "Tasks to skip:"
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
    res = []
    for node in nodes:
        res.append(node['id'])
    return res

   

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
   print
   print "Tasks to execute:" 
   for t in tasks:
       print t
nodes = get_nodes()
if args.verbose:
   print 
   print "Nodes to apply:" 
   for n in nodes:
       print n

node_collection = NodeCollection.init_with_ids(nodes)

if not ok_to_run():
   sys.exit(1)

run = env.execute_tasks(node_collection,tasks)

while True:
   if run.progress == 100:
       break
   print "Progress: {0} Status: {1}".format(run.progress, run.status)
   time.sleep(1)

