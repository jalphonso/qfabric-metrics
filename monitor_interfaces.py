# <*******************
#
# Copyright 2019 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License, which is located at
# http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by the parties, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# Author: Joe Alphonso
# Email: jalphonso@juniper.net
# Version: 1.2.0
# Release Date: 06/17/2019
#
# *******************>

#############################################################################################################################################
#############################################################################################################################################
# IMPORTS
#############################################################################################################################################
#############################################################################################################################################

import csv
import os
import subprocess
import sys
from datetime import datetime
from time import sleep, time
from xml.dom.minidom import parse, parseString
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################


# USER INPUT
polling_interval = 300  # sleep for x seconds before running next command
fte_int_cmd = "cli -c 'show interfaces fabric extensive *fte* | display xml'"
server_int_cmd1 = "cli -c 'show interfaces extensive n00:xe-0/0/[0-1] | display xml'"
server_int_cmd2 = "cli -c 'show interfaces extensive n01:xe-0/0/[0-1] | display xml'"
server_commands = [server_int_cmd1, server_int_cmd2]


#############################################################################################################################################
#############################################################################################################################################
# DO NOT EDIT ANYTHING BELOW HERE
#############################################################################################################################################
#############################################################################################################################################

header = ['interface', 'snmp-index', 'timestamp', 'input_bytes', 'input_packets', 'output_bytes', 'output_packets',
          'input_drops', 'input_errors', 'output_drops', 'output_errors', 'input_bps', 'output_bps']


def write_to_csv(filename, header=None, lines=None):
  try:
    filename = "csv/" + filename.replace('/', '-').replace(':', '-') + ".csv"
    newfile = os.path.exists(filename)
    f = open(filename, 'a+')
    try:
      writer = csv.writer(f)
      if header and not newfile:
        writer.writerow(header)
      if lines:
        writer.writerows(lines)
    finally:
      f.close()
  except IOError:
    print("PID %s: Failed to write to csv named '%s'" % (os.getpid(), filename))


def sleep_with_countdown(sleep_time):
  if sleep_time > 50:
    inc = 10
  elif sleep_time <= 10:
    inc = 1
  else:
    inc = 5
  sys.stdout.write('Countdown until next run: ' + ' ')
  for i in xrange(sleep_time, 0, -1*inc):
    sys.stdout.write(str(i)+' ')
    sys.stdout.flush()
    sleep(inc)
  print('\n')


def process_cmd(command, timestamp=None):
  data = []
  ibytes = ipackets = obytes = opackets = idrops = ierrs = odrops = oerrs = ibps = obps = None

  # adding ability to pass in timestamp so multiple commands (i.e. server with interfaces to multiple switches)
  # use the same timestamp to allow proper post processing of aggregate data
  if not timestamp:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

  time_before_cmd = datetime.utcnow()
  print("PID %s: Retrieving Interface data from Fabric..." % os.getpid())
  iface_xml = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
  time_after_cmd = datetime.utcnow()
  cmd_run_time = time_after_cmd - time_before_cmd
  cmd_run_secs = int(round(cmd_run_time.seconds + float(cmd_run_time.microseconds)/1000000))
  print("PID %s: The QFabric command %s took %d seconds to run under PID %s" % (os.getpid(), command, cmd_run_secs))

  try:
    dom1 = parseString(iface_xml)
  except:
    # If error (most likely didn't get proper xml back from cli), print out xml if any and stop processing this command
    # for this interval
    print("PID %s: XML Error: %s" % (os.getpid(), iface_xml))
    return

  interfaces = dom1.getElementsByTagName('physical-interface')
  if not interfaces:
    print("PID %s: No interfaces found; check QFabric health" % os.getpid())
    return

  for interface in interfaces:
    interface_name = interface.getElementsByTagName('name')[0].firstChild.data
    write_to_csv(interface_name, header=header)
    snmp_if_index = interface.getElementsByTagName('snmp-index')[0].firstChild.data
    stats = interface.getElementsByTagName('ethernet-mac-statistics')
    if stats:
      stat = stats[0]
      ibytes = stat.getElementsByTagName('input-bytes')[0].firstChild.data
      ipackets = stat.getElementsByTagName('input-packets')[0].firstChild.data
      obytes = stat.getElementsByTagName('output-bytes')[0].firstChild.data
      opackets = stat.getElementsByTagName('output-packets')[0].firstChild.data

    input_errs = interface.getElementsByTagName('input-error-list')
    if input_errs:
      err = input_errs[0]
      idrops = err.getElementsByTagName('input-drops')[0].firstChild.data
      ierrs = err.getElementsByTagName('input-errors')[0].firstChild.data

    output_errs = interface.getElementsByTagName('output-error-list')
    if output_errs:
      err = output_errs[0]
      odrops = err.getElementsByTagName('output-drops')[0].firstChild.data
      oerrs = err.getElementsByTagName('output-errors')[0].firstChild.data

    traffic_stats = interface.getElementsByTagName('traffic-statistics')
    if traffic_stats:
      stat = traffic_stats[0]
      ibps = stat.getElementsByTagName('input-bps')[0].firstChild.data
      obps = stat.getElementsByTagName('output-bps')[0].firstChild.data

    data.append([interface_name, snmp_if_index, timestamp, ibytes, ipackets,
                 obytes, opackets, idrops, ierrs, odrops, oerrs, ibps, obps])
    write_to_csv(interface_name, lines=data)


def main():
  while True:
    try:
      awake_time_begin = time()
      print(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
      process_cmd(fte_int_cmd)

      child_pids = []
      # handling server command collection separately
      for server_command in server_commands:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        # using multiprocessing to ensure groups of interfaces are collected as close to the same time as possible
        pid = os.fork()
        if pid:
          child_pids.append(pid)
          continue  # parent continues the loop to spawn the next process for any remaining commands
        print("Child pid is %s and my cmd is %s" % (os.getpid(), server_command))
        process_cmd(server_command, timestamp)
        print("Child pid %s is exiting..." % os.getpid())
        sys.exit()  # child exits
      # parent waits for each of the children before completing this iteration
      for idx, child_pid in enumerate(child_pids):
        pid, status = os.waitpid(child_pid, 0)
        print("wait #%d returned for child pid %d" % (idx, pid))
      print("Run completed at %s" % datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
      awake_time_end = time()
      awake_time = int(awake_time_end - awake_time_begin)
      if polling_interval > awake_time:
        print("%s seconds until the next run. Ctrl+c to quit" % (polling_interval - awake_time))
        sleep_with_countdown(polling_interval - awake_time)
      else:
        print("%s seconds until the next run. Ctrl+c to quit" % polling_interval)
        sleep_with_countdown(polling_interval)
    except KeyboardInterrupt:
      print("\nQuitting per user's request...")
      sys.exit(0)


if __name__ == "__main__":
  main()
