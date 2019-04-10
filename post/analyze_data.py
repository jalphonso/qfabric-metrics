import csv
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
import time

csv_path = "csv"

start = time.time()

def average(num_list):
  return round(float(sum(num_list))/len(num_list),2)


try:
  csv_files = [f for f in listdir(csv_path) if isfile(join(csv_path, f)) and os.path.splitext(f)[-1]=='.csv']
  for filename in csv_files:

    #Intialize dataset to empty lists
    input_bytes = [] #index 3
    input_packets = [] #index 4
    output_bytes = []  #index 5
    output_packets = [] #index 6
    input_drops = [] #index 7
    input_errors = [] #index 8
    output_drops = [] #index 9
    output_errors = [] #index 10
    input_bps = [] #index 11
    output_bps = [] #index 12

    f = open(os.path.join(csv_path, filename), 'r')
    try:
      reader = csv.reader(f)
      first = True
      for row in reader:
        if first:
          first = False
          continue
        interface = row[0]
        input_bps.append(int(row[11]))
        output_bps.append(int(row[12]))
      print("Interface      input_bps(min)     input_bps(max)     input_bps(avg)      output_bps(min)     output_bps(max)      output_bps(avg)")
      print("%15s %10.2f" % (interface, average(input_bps)))
      #print(min(input_bps))
      #print(average(input_bps))
      #print(max(input_bps))
      #print(min(output_bps))
      #print(max(output_bps))
    finally:
      f.close()
except IOError:
  print("Failed to read file")

end = time.time()
print("Post processing took %s seconds to run" % (end - start))
