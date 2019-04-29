from interface_stats import InterfaceStats
from os import listdir
from os.path import isfile, join
import csv
import os
import time

csv_path = "csv"
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
fields = [input_bytes_name, output_bytes_name, input_packets_name, output_packets_name, input_drops_name, output_drops_name,
          input_errors_name, output_errors_name, input_bps_name, output_bps_name]
data = {}
devices = []
interfaces = []


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
    csv_files = [f for f in listdir(csv_path) if isfile(join(csv_path, f)) and os.path.splitext(f)[-1]=='.csv']
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


def generate_report():
  time_interval = 'hour'
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
          processed_dataset[node] = []

        results_by_time = list(get_data_for_time_interval(data[node][field], time_interval))
        for results in results_by_time:
          for timestamp, dataset in results.items():
            if 'bps' in field:
              processed_dataset[node].append({timestamp:{'min':min(dataset),
                                                          'max':max(dataset),
                                                          'avg':average(dataset)}})
            else:
              processed_dataset[node].append({timestamp:{'avg':average_counters(dataset, seconds[time_interval])}})

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
      f = open("reports/" + report + ".txt", 'w')
      try:
        if 'bps' in report:
          f.write("Node              YYYY-mm-dd HH      min_input%(unit)-11s max_input%(unit)-11s avg_input%(unit)-11s "
                  "min_output%(unit)-11s max_output%(unit)-11s avg_output%(unit)s\n" % {'unit':unit})
        else:
          f.write("Node              YYYY-mm-dd HH      avg_input%(unit)-13s avg_output%(unit)s\n" % {'unit':unit})
        for node_set in node_sets:
          for node in node_set:
            dev_in_data = sorted(eval('input_' + suffix + '_node_processed_dataset')[node])
            dev_out_data = sorted(eval('output_' + suffix + '_node_processed_dataset')[node])
            for idx, dataset in enumerate(dev_in_data):
              for timestamp, in_data in dataset.items():
                out_data = dev_out_data[idx][timestamp]
                if 'bps' in report:
                  f.write("%-17s %-18s %-20.2f %-20.2f %-20.2f %-21.2f %-21.2f %-0.2f\n" \
                          % (node, timestamp, in_data['min'], in_data['max'], in_data['avg'],
                            out_data['min'], out_data['max'], out_data['avg']))
                else:
                  f.write("%-17s %-18s %-22.2f %-0.2f\n" % (node, timestamp, in_data['avg'], out_data['avg']))
      finally:
        f.close()
    except IOError:
      print("Failed to write report; Make sure reports dir exists")


if __name__ == "__main__":
  start = time.time()
  csvs_to_dict()
  generate_report()
  end = time.time()
  print("Post processing took %s seconds to run" % (end - start))
