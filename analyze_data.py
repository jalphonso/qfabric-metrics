# <*******************
#
# Copyright 2019 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License, which is located at
# http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by the parties, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.
#
# Author: Joe Alphonso
# Email: jalphonso@juniper.net
# Version: 1.1.2
# Release Date: 06/07/2019
#
# *******************>
from interface_stats import InterfaceStats
from os import listdir
from os.path import isfile, join
import copy
import csv
import json
import os
import time

#User Input
csv_path = "csv2"
report_path = "reports2"
bps_threshold = 1024*1024*1024*15
TIME_INTERVAL = 'hour' #choices are hour or day

input_bytes_name = 'input_bytes'
input_packets_name = 'input_packets'
output_bytes_name = 'output_bytes'
output_packets_name = 'output_packets'
input_drops_name = 'input_drops'
input_errors_name = 'input_errors'
output_drops_name = 'output_drops'
output_errors_name = 'output_errors'
input_bps_name = 'input_bps'
output_bps_name = 'output_bps'
fields = [input_bytes_name, output_bytes_name, input_packets_name, output_packets_name, input_drops_name,
          output_drops_name, input_errors_name, output_errors_name, input_bps_name, output_bps_name]
data = {}
node_report_data = {}
devices = []
interfaces = []


def bps_to_human(num, suffix='bps'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.2f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.2f%s%s" % (num, 'Y', suffix)


def average(num_list):
  return round(float(sum(num_list))/len(num_list),2)


def average_counters(counter_list, seconds):
  return round((float(max(counter_list)) - float(min(counter_list)))/seconds, 2)


def get_data_for_time_interval(d, time_interval='minute'):
  sub_data = []
  for year, months in d.items():
    for month, days in months.items():
      for day, hours in days.items():
        for hour, minutes in hours.items():
          for minute, seconds in minutes.items():
            for second, data_rows in seconds.items():
              device_total = 0
              for row in data_rows:
                #sum counters for all interfaces belonging to this device
                device_total = device_total + row['data']
              sub_data.append(device_total)
              if time_interval == 'second':
                date_string = ("%(year)s-%(month)s-%(day)s %(hour)s:%(minute)s:%(second)s" %
                              {'year':year, 'month':month, 'day':day, 'hour':hour, 'minute':minute, 'second':second})
                yield {date_string: sub_data}
                sub_data = []
            if time_interval == 'minute':
              date_string = ("%(year)s-%(month)s-%(day)s %(hour)s:%(minute)s" %
                            {'year':year, 'month':month, 'day':day, 'hour':hour, 'minute':minute})
              yield {date_string: sub_data}
              sub_data = []
          if time_interval == 'hour':
            date_string = ("%(year)s-%(month)s-%(day)s %(hour)s" %
                          {'year':year, 'month':month, 'day':day, 'hour':hour})
            yield {date_string: sub_data}
            sub_data = []
        if time_interval == 'day':
          date_string = ("%(year)s-%(month)s-%(day)s" %
                        {'year':year, 'month':month, 'day':day})
          yield {date_string: sub_data}
          sub_data = []
      if time_interval == 'month':
        date_string = ("%(year)s-%(month)s" %
                      {'year':year, 'month':month})
        yield {date_string: sub_data}
        sub_data = []
    if time_interval == 'year':
      date_string = ("%(year)s" %
                    {'year':year})
      yield {date_string: sub_data}
      sub_data = []


def create_dict_key(data_dict, key, key_type):
  if key not in data_dict and key_type == 'dict':
    data_dict[key] = {}
  elif key not in data_dict and key_type == 'list':
    data_dict[key] = []
  return data_dict[key]


def parse_date_time(timestamp):
  p_date, p_time = timestamp.split(' ')
  year, month, day = p_date.split('-')
  hour, minute, second = p_time.split(':')

  time_elements = [year, month, day, hour, minute, second]
  return time_elements


def csvs_to_dict():
  try:
    csv_files = [f for f in listdir(csv_path) if isfile(join(csv_path, f))
                 and os.path.splitext(f)[-1]=='.csv' and 'xe-' not in f]
    for filename in csv_files:
      fparts = filename.split('-')
      if 'IC' in filename:
        device =  fparts[0] + '-' + fparts[1]
      else:
        device =  fparts[0]

      #keep track of devices in global list
      if device not in devices:
        devices.append(device)

      # add device to data dictionary if not present
      if device not in data:
        data[device] = {}

      f = open(os.path.join(csv_path, filename), 'r')
      try:
        reader = csv.reader(f)
        first = True
        for row in reader:
          if first:
            first = False
            continue

          int_obj = InterfaceStats(*row)

          interface = int_obj.interface
          timestamp = int_obj.timestamp

          #keep track of interfaces in global list
          if interface not in interfaces:
            interfaces.append(interface)
          # add device to data dictionary if not present
          if interface not in data:
            data[interface] = {}

          for field in fields:
            # add keys to data dictionary if not present
            if field not in data[device]:
              data[device][field] = {}
            if field not in data[interface]:
              data[interface][field] = {}

            time_elements = parse_date_time(timestamp)

            time_dict_dev = data[device][field]
            time_dict_int = data[interface][field]
            # add timestamp to data dictionary if not present
            for idx, ele in enumerate(time_elements):
              if idx < 5:
                time_dict_dev = create_dict_key(time_dict_dev, ele, 'dict')
                time_dict_int = create_dict_key(time_dict_int, ele, 'dict')
              else:
                time_dict_dev = create_dict_key(time_dict_dev, ele, 'list')
                time_dict_int = create_dict_key(time_dict_int, ele, 'list')
                #Save counters to data structure
                data_value = getattr(int_obj, field)
                if data_value:
                  time_dict_dev.append({'interface': interface, 'data': int(data_value)})
                  time_dict_int.append({'data': int(data_value)})
                else:
                  time_dict_dev.append({'interface': interface, 'data': 0})
                  time_dict_int.append({'data': 0})
      finally:
        f.close()
  except IOError:
    print("Failed to read file")


def generate_reports():
  time_interval = TIME_INTERVAL
  seconds = {'hour': 3600, 'day': 86400}

  #Intialize dataset to empty dicts
  input_bytes_node_processed_dataset = {}
  input_packets_node_processed_dataset = {}
  output_bytes_node_processed_dataset = {}
  output_packets_node_processed_dataset = {}
  input_drops_node_processed_dataset = {}
  input_errors_node_processed_dataset = {}
  output_drops_node_processed_dataset = {}
  output_errors_node_processed_dataset = {}
  input_bps_node_processed_dataset = {}
  output_bps_node_processed_dataset = {}

  node_sets = [devices, interfaces]
  for node_set in node_sets:
    for node in node_set:
      for field in fields:
        processed_dataset = eval(field + '_node_processed_dataset')
        if node not in processed_dataset:
          processed_dataset[node] = {}

        results_by_time = list(get_data_for_time_interval(data[node][field], time_interval))
        for results in results_by_time:
          for timestamp, dataset in results.items():
            if 'bps' in field:
              processed_dataset[node][timestamp] = {'min':min(dataset),
                                                    'max':max(dataset),
                                                    'avg':average(dataset)}
            else:
              processed_dataset[node][timestamp] = {'avg':average_counters(dataset, seconds[time_interval])}

  reports = ['report_bps', 'report_packets', 'report_bytes', 'report_drops', 'report_errors']
  for report in reports:
    suffix = report.split('_')[1]
    if 'byte' in suffix:
      unit = '(bytes/sec)'
    elif 'packet' in suffix:
      unit = '(packets/sec)'
    elif 'drop' in suffix:
      unit = '(drops/sec)'
    elif 'error' in suffix:
      unit = '(errors/sec)'
    else:
      unit = '(bits/sec)'

    try:
      f = open(report_path + "/" + report + ".txt", 'w')
      try:
        if 'bps' in report:
          f.write("Node              YYYY-mm-dd HH      min_input%(unit)-11s max_input%(unit)-11s avg_input%(unit)-11s "
                  "min_output%(unit)-11s max_output%(unit)-11s avg_output%(unit)s\n" % {'unit':unit})
        else:
          f.write("Node              YYYY-mm-dd HH      avg_input%(unit)-13s avg_output%(unit)s\n" % {'unit':unit})
        for node_set in node_sets:
          for node in node_set:
            dev_in_data = eval('input_' + suffix + '_node_processed_dataset')[node]
            dev_out_data = eval('output_' + suffix + '_node_processed_dataset')[node]
            for timestamp, in_data in dev_in_data.items():
              out_data = dev_out_data[timestamp]
              if 'bps' in report:
                f.write("%-17s %-18s %-20d %-20d %-20d %-21d %-21d %d\n" \
                        % (node, timestamp, in_data['min'], in_data['max'], in_data['avg'],
                          out_data['min'], out_data['max'], out_data['avg']))
              else:
                f.write("%-17s %-18s %-22.2f %-0.2f\n" % (node, timestamp, in_data['avg'], out_data['avg']))
      finally:
        f.close()
    except IOError:
      print("Failed to write report; Make sure reports dir exists")


def analyze_reports():
  try:
    f = open(report_path + "/report_bps.txt", 'r')
    try:
      f.readline() #throw away header
      lines = f.readlines()
      for line in lines:
        row = line.split()
        node = row[0]
        i_max = int(row[4])
        o_max = int(row[7])

        if node not in node_report_data:
          node_report_data[node] = {}

        if ('i_max' not in node_report_data[node] or not node_report_data[node]['i_max']
            or i_max > node_report_data[node]['i_max']):
          node_report_data[node]['i_max'] = i_max
        if ('o_max' not in node_report_data[node] or not node_report_data[node]['o_max']
            or o_max > node_report_data[node]['o_max']):
          node_report_data[node]['o_max'] = o_max

    finally:
      f.close()
  except IOError:
    print("Failed to read report_bps.txt; Make sure report exists")

  try:
    f = open(report_path + "/report_bytes.txt", 'r')
    try:
      f.readline() #throw away header
      lines = f.readlines()
      for line in lines:
        row = line.split()
        node = row[0]
        i_avg = int(float(row[3]) * 8)
        o_avg = int(float(row[4]) * 8)

        if node not in node_report_data:
          node_report_data[node] = {}

        if ('i_avg' not in node_report_data[node] or not node_report_data[node]['i_avg']
            or i_avg > node_report_data[node]['i_avg']):
          node_report_data[node]['i_avg'] = i_avg
        if ('o_avg' not in node_report_data[node] or not node_report_data[node]['o_avg']
            or o_avg > node_report_data[node]['o_avg']):
          node_report_data[node]['o_avg'] = o_avg
    finally:
      f.close()
  except IOError:
    print("Failed to read report_bytes.txt; Make sure report exists")

  try:
    f = open(report_path + "/report_drops.txt", 'r')
    try:
      f.readline() #throw away header
      lines = f.readlines()
      for line in lines:
        row = line.split()
        node = row[0]
        i_drops = int(float(row[3]))
        o_drops = int(float(row[4]))

        if node not in node_report_data:
          node_report_data[node] = {}

        if ('i_drops' not in node_report_data[node] or not node_report_data[node]['i_drops']
             or i_drops > node_report_data[node]['i_drops']):
          node_report_data[node]['i_drops'] = i_drops
        if ('o_drops' not in node_report_data[node] or not node_report_data[node]['o_drops']
            or o_drops > node_report_data[node]['o_drops']):
          node_report_data[node]['o_drops'] = o_drops
    finally:
      f.close()
  except IOError:
    print("Failed to read report_drops.txt; Make sure report exists")

  try:
    f = open(report_path + "/report_errors.txt", 'r')
    try:
      f.readline() #throw away header
      lines = f.readlines()
      for line in lines:
        row = line.split()
        node = row[0]
        i_errors = int(float(row[3]))
        o_errors = int(float(row[4]))

        if node not in node_report_data:
          node_report_data[node] = {}

        if ('i_errors' not in node_report_data[node] or not node_report_data[node]['i_errors']
            or i_errors > node_report_data[node]['i_errors']):
          node_report_data[node]['i_errors'] = i_errors
        if ('o_errors' not in node_report_data[node] or not node_report_data[node]['o_errors']
            or o_errors > node_report_data[node]['o_errors']):
          node_report_data[node]['o_errors'] = o_errors
    finally:
      f.close()
  except IOError:
    print("Failed to read report_errors.txt; Make sure report exists")


def print_and_save_summary():
  node_report_data_human = {}
  print("\nSUMMARY")
  for node, values in node_report_data.items():
    if values['i_drops']:
      print("Node %s has input drops" % node)
    if values['o_drops']:
      print("Node %s has output drops" % node)
    if values['i_errors']:
      print("Node %s has input errors" % node)
    if values['o_errors']:
      print("Node %s has output errors" % node)
    if values['o_avg'] > bps_threshold or values['o_max'] > bps_threshold:
      print("Node %s has exceeded the bps_threshold of %s for outbound traffic" % (node, bps_to_human(bps_threshold)))
    if values['i_avg'] > bps_threshold or values['i_max'] > bps_threshold:
      print("Node %s has exceeded the bps_threshold of %s for inbound traffic" % (node, bps_to_human(bps_threshold)))

    node_report_data_human[node] = {}
    for k, v in values.items():
      if 'err' in k:
        node_report_data_human[node][k] = str(v) + ' errors/sec'
      elif 'drop' in k:
        node_report_data_human[node][k] = str(v) + ' drops/sec'
      else:
        node_report_data_human[node][k] = bps_to_human(v)

  with open(report_path + "/summary.json", 'w') as f:
    json.dump(sorted(node_report_data_human.items()), f)

def get_node(d, val, key):
  for k, v in d.items():
    if v[key] == val:
      return k
  return "Node not found for key %s and value %s" % (key, val)

def print_top_talkers():
  #print(node_report_data)
  for key in ['i_max', 'o_max', 'i_avg', 'o_avg']:
    if key == 'i_max':
      print("\nHIGHEST INPUT BURSTS")
      friendly_key = 'input burst'
    if key == 'o_max':
      print("\nHIGHEST OUTPUT BURSTS")
      friendly_key = 'output burst'
    if key == 'i_avg':
      print("\nHIGHEST INPUT AVERAGES")
      friendly_key = 'input average'
    if key == 'o_avg':
      print("\nHIGHEST OUTPUT AVERAGES")
      friendly_key = 'output average'
    temp_dict = copy.deepcopy(node_report_data)
    for i in range(10):
      max_val = max(d[key] for d in temp_dict.values())
      node = get_node(temp_dict, max_val, key)
      print("Node %s is the #%s talker with an %s of %s" % (node, i+1, friendly_key, bps_to_human(max_val)))
      temp_dict.pop(node)


if __name__ == "__main__":
  start = time.time()
  csvs_to_dict()
  generate_reports()
  analyze_reports()
  print_and_save_summary()
  print_top_talkers()
  end = time.time()
  print("\nPost processing took %s seconds to run" % (end - start))
