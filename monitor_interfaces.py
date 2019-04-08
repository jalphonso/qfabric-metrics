import csv
import os
import subprocess
import sys
from datetime import datetime
from time import sleep
from xml.dom.minidom import parse, parseString

polling_interval = 300 # sleep for x seconds before running next command
header = ['interface', 'snmp-index', 'timestamp', 'input_bytes', 'input_packets', 'output_bytes', 'output_packets',
          'input_drops', 'input_errors', 'output_drops', 'output_errors', 'input_bps', 'output_bps']
data = []
ibytes = ipackets = obytes = opackets = idrops = ierrs = odrops = oerrs = ibps = obps = None

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
    print("Failed to write to csv")

def sleep_with_countdown(sleep_time):
  if sleep_time > 50:
    inc = 10
  elif sleep_time <= 10:
    inc = 1
  else:
    inc = 5
  sys.stdout.write('Countdown until next run: ' + ' ')
  for i in xrange(sleep_time,0, -1*inc):
    sys.stdout.write(str(i)+' ')
    sys.stdout.flush()
    sleep(inc)
  print('\n')

try:
  while(True):
    print(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    time_before_cmd = datetime.utcnow()
    print("Retrieving Interface data from Fabric...")
    iface_xml = subprocess.Popen("cli -c 'show interfaces fabric extensive *fte* | display xml'", shell=True, stdout=subprocess.PIPE).stdout.read()
    time_after_cmd = datetime.utcnow()
    cmd_run_time = time_after_cmd - time_before_cmd
    cmd_run_secs = int(round(cmd_run_time.seconds + float(cmd_run_time.microseconds)/1000000))
    print("The QFabric command 'show interfaces fabric extensive *fte*' took %d seconds to run" % cmd_run_secs)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    dom1 = parseString(iface_xml)
    interfaces = dom1.getElementsByTagName('physical-interface')
    for interface in interfaces:
      interface_name = interface.getElementsByTagName('name')[0].firstChild.data
      write_to_csv(interface_name, header=header)
      snmp_if_index = interface.getElementsByTagName('snmp-index')[0].firstChild.data
      stats = interface.getElementsByTagName('ethernet-mac-statistics')
      if(stats):
        stat = stats[0]
        ibytes = stat.getElementsByTagName('input-bytes')[0].firstChild.data
        ipackets = stat.getElementsByTagName('input-packets')[0].firstChild.data
        obytes = stat.getElementsByTagName('output-bytes')[0].firstChild.data
        opackets = stat.getElementsByTagName('output-packets')[0].firstChild.data

      input_errs = interface.getElementsByTagName('input-error-list')
      if(input_errs):
        err = input_errs[0]
        idrops = err.getElementsByTagName('input-drops')[0].firstChild.data
        ierrs = err.getElementsByTagName('input-errors')[0].firstChild.data

      output_errs = interface.getElementsByTagName('output-error-list')
      if(output_errs):
        err = output_errs[0]
        odrops = err.getElementsByTagName('output-drops')[0].firstChild.data
        oerrs = err.getElementsByTagName('output-errors')[0].firstChild.data

      traffic_stats = interface.getElementsByTagName('traffic-statistics')
      if traffic_stats:
        stat = traffic_stats[0]
        ibps = stat.getElementsByTagName('input-bps')[0].firstChild.data
        obps = stat.getElementsByTagName('output-bps')[0].firstChild.data

      data.append([interface_name, snmp_if_index, timestamp, ibytes, ipackets, obytes, opackets, idrops, ierrs, odrops, oerrs, ibps, obps])
      write_to_csv(interface_name, lines=data)

      #empty out dataset for next run
      data = []
      ibytes = ipackets = obytes = opackets = idrops = ierrs = odrops = oerrs = ibps = obps = None

    print("Run completed at %s" % datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    print("%s seconds until the next run. Ctrl+c to quit" % polling_interval)
    sleep_with_countdown(polling_interval)
except KeyboardInterrupt:
  print("\nQuitting per user's request...")
  sys.exit(0)
